# ui/dialogs.py
# Dialog windows for RetroArch Rom Manager

import os
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QProgressBar,
    QFrame, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from .widgets import StyledButton, SectionLabel, CardFrame


class GroovySyncDialog(QDialog):
    """Dialog for Groovy sync status and progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("그루비 동기화")
        self.setFixedSize(350, 150)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status label
        self.status_label = QLabel("그루비 서버에 접속중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = StyledButton("취소", "red")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def set_status(self, message: str):
        """Update status message."""
        self.status_label.setText(message)

    def set_progress(self, value: int):
        """Update progress bar value (0-100)."""
        self.progress_bar.setValue(value)

    def finish_success(self):
        """Mark sync as complete."""
        self.status_label.setText("동기화 완료!")
        self.progress_bar.setValue(100)
        self.cancel_button.setText("닫기")
        self.cancel_button.setProperty('class', 'green')
        self.cancel_button.style().unpolish(self.cancel_button)
        self.cancel_button.style().polish(self.cancel_button)


IMAGE_TYPE_LABELS = {
    'ss': '스크린샷',
    'sstitle': '타이틀 화면',
    'box-2D': '박스아트 2D',
    'box-3D': '박스아트 3D',
    'wheel': '휠 아트',
    'wheel-hd': '휠 아트 HD',
    'fanart': '팬아트',
    'screenmarquee': '마키',
    'screenmarqueesmall': '마키 (소)',
    'steamgrid': '스팀 그리드',
    'support-2D': '미디어 2D',
    'support-3D': '미디어 3D',
}


class ScrapWorker(QThread):
    """게임 검색 전용 워커 — 다운로드 없이 메타데이터·이미지 목록만 반환."""

    log = Signal(str)
    finished = Signal(bool, dict, list)  # success, game_info, image_list

    def __init__(self, rom_full_path, rom_name, system_id):
        super().__init__()
        self.rom_full_path = rom_full_path
        self.rom_name = rom_name
        self.system_id = system_id

    def run(self):
        from screenScraper import ScreenScraperAPI

        api = ScreenScraperAPI()
        self.log.emit(f"검색 중: {self.rom_name}")

        game_data = api.searchGame(self.rom_full_path, self.system_id, self.rom_name)
        if game_data is None:
            self.log.emit("게임을 찾을 수 없습니다.")
            self.finished.emit(False, {}, [])
            return

        game_info = api.getGameInfo(game_data, lang='ko')
        image_list = api.getAllGameImages(game_data)

        self.log.emit("=== 검색 결과 ===")
        self.log.emit(f"게임 이름: {game_info.get('name', 'N/A')}")
        self.log.emit(f"개발사: {game_info.get('developer', 'N/A')}")
        self.log.emit(f"퍼블리셔: {game_info.get('publisher', 'N/A')}")
        self.log.emit(f"장르: {game_info.get('genre', 'N/A')}")
        self.log.emit(f"출시일: {game_info.get('releasedate', 'N/A')}")
        self.log.emit(f"이미지 후보: {len(image_list)}개")
        self.finished.emit(True, game_info, image_list)


class ImageFetchWorker(QThread):
    """선택된 이미지 URL을 임시 파일로 다운로드해 미리보기 제공."""

    finished = Signal(bytes)  # 이미지 바이트 데이터

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        from screenScraper import ScreenScraperAPI
        import requests

        api = ScreenScraperAPI()
        params = {'devid': api.devid, 'devpassword': api.devpassword, 'softname': api.softname}
        if api.ssid:
            params['ssid'] = api.ssid
        if api.sspassword:
            params['sspassword'] = api.sspassword
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(self.url, params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                self.finished.emit(r.content)
            else:
                self.finished.emit(b'')
        except Exception:
            self.finished.emit(b'')


class ImageScrapDialog(QDialog):
    """ScreenScraper 이미지 스크랩 다이얼로그 — 이미지 후보 선택 지원."""

    def __init__(self, game: dict, system_id: int, sub_rom_dir: str, parent=None):
        super().__init__(parent)
        self.game = game
        self.system_id = system_id
        self.sub_rom_dir = sub_rom_dir
        self.xml_manager = None
        self._scrap_worker = None
        self._fetch_worker = None
        self._game_info = {}
        self._image_list = []          # [{'type','region','url'}, ...]
        self._selected_url = None
        self._preview_bytes = None     # 현재 미리보기 이미지 바이트

        from config import Config
        config = Config()
        rom_filename = os.path.basename(game['path'])
        rom_stem = os.path.splitext(rom_filename)[0]
        self._rom_full_path = os.path.join(config.getBasePath(), sub_rom_dir, rom_filename)
        self._image_save_path = os.path.join(
            config.getBasePath(), sub_rom_dir, 'media', 'images', rom_stem + '.png'
        )

        self.setWindowTitle("이미지 스크랩")
        self.setMinimumSize(780, 620)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # 게임 정보
        info_frame = CardFrame()
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(6)
        info_layout.addWidget(QLabel("게임 이름:"), 0, 0, Qt.AlignRight)
        info_layout.addWidget(QLabel(self.game.get('name', 'N/A')), 0, 1, Qt.AlignLeft)
        info_layout.addWidget(QLabel("ROM 파일:"), 1, 0, Qt.AlignRight)
        info_layout.addWidget(QLabel(os.path.basename(self.game.get('path', ''))), 1, 1, Qt.AlignLeft)
        info_layout.addWidget(QLabel("시스템:"), 2, 0, Qt.AlignRight)
        system_text = f"{self.sub_rom_dir} (ID: {self.system_id})" if self.system_id else self.sub_rom_dir
        info_layout.addWidget(QLabel(system_text), 2, 1, Qt.AlignLeft)
        layout.addWidget(info_frame)

        # 본문: 이미지 목록 | 미리보기
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)

        # 왼쪽: 이미지 목록
        list_frame = CardFrame()
        list_vbox = QVBoxLayout(list_frame)
        list_vbox.addWidget(SectionLabel("이미지 후보"))
        self.image_list_widget = QListWidget()
        self.image_list_widget.setMinimumWidth(200)
        self.image_list_widget.currentItemChanged.connect(self._on_image_selected)
        list_vbox.addWidget(self.image_list_widget)
        body_layout.addWidget(list_frame, 2)

        # 오른쪽: 미리보기 + 로그
        right_vbox = QVBoxLayout()
        right_vbox.setSpacing(8)

        self.preview_label = QLabel("이미지를 선택하면\n미리보기가 표시됩니다")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 250)
        self.preview_label.setStyleSheet("border: 1px solid #444; background: #1a1a2e; color: #888;")
        right_vbox.addWidget(self.preview_label, 3)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        right_vbox.addWidget(self.status_text, 1)

        body_layout.addLayout(right_vbox, 3)
        layout.addLayout(body_layout)

        # 버튼
        button_layout = QHBoxLayout()

        self.search_button = StyledButton("검색", "blue")
        self.search_button.clicked.connect(self._do_search)
        button_layout.addWidget(self.search_button)

        self.save_button = StyledButton("이 이미지로 저장", "green")
        self.save_button.clicked.connect(self._do_save)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        self.update_info_button = StyledButton("정보 업데이트", "default")
        self.update_info_button.clicked.connect(self._do_update_info)
        self.update_info_button.setEnabled(False)
        button_layout.addWidget(self.update_info_button)

        button_layout.addStretch()

        self.close_button = StyledButton("닫기", "default")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def set_xml_manager(self, xml_manager):
        self.xml_manager = xml_manager

    def log_status(self, message: str):
        self.status_text.append(message)
        self.status_text.ensureCursorVisible()

    # ── 검색 ──────────────────────────────────────────────

    def _do_search(self):
        from screenScraper import ScreenScraperAPI

        if not ScreenScraperAPI().isConfigured():
            self.log_status("오류: secret.ini에 ScreenScraperDevID/DevPassword를 추가하세요.")
            return
        if self.system_id is None:
            self.log_status(f"오류: '{self.sub_rom_dir}' 시스템 ID를 찾을 수 없습니다.")
            return

        self.search_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.update_info_button.setEnabled(False)
        self.image_list_widget.clear()
        self.preview_label.setText("검색 중...")
        self.status_text.clear()

        self._scrap_worker = ScrapWorker(
            self._rom_full_path,
            os.path.basename(self.game['path']),
            self.system_id,
        )
        self._scrap_worker.log.connect(self.log_status)
        self._scrap_worker.finished.connect(self._on_search_finished)
        self._scrap_worker.start()

    def _on_search_finished(self, success: bool, game_info: dict, image_list: list):
        self.search_button.setEnabled(True)

        if not success:
            self.preview_label.setText("검색 실패")
            return

        self._game_info = game_info
        self._image_list = image_list
        self.update_info_button.setEnabled(True)
        self.preview_label.setText("이미지를 선택하세요")

        self.image_list_widget.clear()
        for entry in image_list:
            label = IMAGE_TYPE_LABELS.get(entry['type'], entry['type'])
            region = entry['region']
            item = QListWidgetItem(f"{label}  [{region}]")
            item.setData(Qt.UserRole, entry['url'])
            self.image_list_widget.addItem(item)

        if self.image_list_widget.count() > 0:
            self.image_list_widget.setCurrentRow(0)

    # ── 이미지 선택 → 미리보기 ──────────────────────────────

    def _on_image_selected(self, current, _previous):
        if current is None:
            return
        url = current.data(Qt.UserRole)
        self._selected_url = url
        self.save_button.setEnabled(False)
        self.preview_label.setText("불러오는 중...")

        if self._fetch_worker and self._fetch_worker.isRunning():
            self._fetch_worker.terminate()

        self._fetch_worker = ImageFetchWorker(url)
        self._fetch_worker.finished.connect(self._on_preview_ready)
        self._fetch_worker.start()

    def _on_preview_ready(self, data: bytes):
        if not data:
            self.preview_label.setText("미리보기 불러오기 실패")
            return

        self._preview_bytes = data
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.preview_label.setPixmap(scaled)
            self.save_button.setEnabled(True)
        else:
            self.preview_label.setText("이미지 형식 오류")

    # ── 저장 ──────────────────────────────────────────────

    def _do_save(self):
        if not self._preview_bytes:
            return

        os.makedirs(os.path.dirname(self._image_save_path), exist_ok=True)
        with open(self._image_save_path, 'wb') as f:
            f.write(self._preview_bytes)
        self.log_status(f"저장 완료: {self._image_save_path}")

        if self.xml_manager:
            rel_image = './media/images/' + os.path.basename(self._image_save_path)
            self.game['image'] = rel_image
            if self._game_info.get('name'):
                self.game['name'] = self._game_info['name']
            if self._game_info.get('description'):
                self.game['desc'] = self._game_info['description']
            self.xml_manager.updateGame(self.game['path'], self.game)
            self.log_status("XML 업데이트 완료!")

    # ── 정보 업데이트 ──────────────────────────────────────

    def _do_update_info(self):
        if not self._game_info:
            return
        result = QMessageBox.question(
            self, "정보 업데이트",
            "검색된 정보로 게임 이름·설명을 업데이트하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if result == QMessageBox.Yes and self.xml_manager:
            if self._game_info.get('name'):
                self.game['name'] = self._game_info['name']
            if self._game_info.get('description'):
                self.game['desc'] = self._game_info['description']
            self.xml_manager.updateGame(self.game['path'], self.game)
            self.log_status("게임 정보가 업데이트되었습니다!")


class ConfirmDialog(QMessageBox):
    """Styled confirmation dialog."""

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)


class InfoDialog(QMessageBox):
    """Styled information dialog."""

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)


class ErrorDialog(QMessageBox):
    """Styled error dialog."""

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Ok)


def show_error(parent, title: str, message: str):
    """Show error message box."""
    QMessageBox.critical(parent, title, message)


def show_info(parent, title: str, message: str):
    """Show information message box."""
    QMessageBox.information(parent, title, message)


def ask_question(parent, title: str, message: str) -> bool:
    """Show question dialog and return True if Yes clicked."""
    result = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return result == QMessageBox.Yes


def get_directory(parent, title: str, initial_dir: str = "") -> str:
    """Show directory selection dialog."""
    return QFileDialog.getExistingDirectory(parent, title, initial_dir)
