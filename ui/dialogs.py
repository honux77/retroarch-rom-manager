# ui/dialogs.py
# Dialog windows for RetroArch Rom Manager

import os
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QProgressBar,
    QFrame, QMessageBox, QFileDialog
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


class ImageScrapDialog(QDialog):
    """Dialog for ScreenScraper image scraping."""

    def __init__(self, game: dict, system_id: int, sub_rom_dir: str, parent=None):
        super().__init__(parent)
        self.game = game
        self.system_id = system_id
        self.sub_rom_dir = sub_rom_dir
        self.xml_manager = None

        self.setWindowTitle("이미지 스크랩")
        self.setMinimumSize(650, 550)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Game info section
        info_frame = CardFrame()
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(8)

        info_layout.addWidget(QLabel("게임 이름:"), 0, 0, Qt.AlignRight)
        info_layout.addWidget(QLabel(self.game.get('name', 'N/A')), 0, 1, Qt.AlignLeft)

        info_layout.addWidget(QLabel("ROM 파일:"), 1, 0, Qt.AlignRight)
        info_layout.addWidget(QLabel(self.game.get('path', 'N/A')), 1, 1, Qt.AlignLeft)

        info_layout.addWidget(QLabel("시스템:"), 2, 0, Qt.AlignRight)
        system_text = f"{self.sub_rom_dir} (ID: {self.system_id})" if self.system_id else self.sub_rom_dir
        info_layout.addWidget(QLabel(system_text), 2, 1, Qt.AlignLeft)

        layout.addWidget(info_frame)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)

        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        layout.addWidget(self.status_text)

        # Preview label
        self.preview_label = QLabel("이미지 미리보기")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        # Button frame
        button_layout = QHBoxLayout()

        self.scrap_button = StyledButton("이미지 스크랩", "green")
        self.scrap_button.clicked.connect(self._do_scrap)
        button_layout.addWidget(self.scrap_button)

        self.info_button = StyledButton("정보만 검색", "blue")
        self.info_button.clicked.connect(self._do_scrap_info)
        button_layout.addWidget(self.info_button)

        button_layout.addStretch()

        self.close_button = StyledButton("닫기", "default")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def set_xml_manager(self, xml_manager):
        """Set XML manager for updating game info."""
        self.xml_manager = xml_manager

    def log_status(self, message: str):
        """Add message to status log."""
        self.status_text.append(message)
        self.status_text.ensureCursorVisible()

    def _do_scrap(self):
        """Execute image scraping."""
        from screenScraper import ScreenScraperAPI

        api = ScreenScraperAPI()

        if not api.isConfigured():
            self.log_status("오류: ScreenScraper 계정이 설정되지 않았습니다.")
            self.log_status("secret.ini 파일에 다음 항목을 추가하세요:")
            self.log_status("  ScreenScraperID = 계정ID")
            self.log_status("  ScreenScraperPassword = 비밀번호")
            return

        if self.system_id is None:
            self.log_status(f"오류: '{self.sub_rom_dir}' 시스템의 ID를 찾을 수 없습니다.")
            return

        rom_full_path = os.path.join(os.getcwd(), self.game['path'])
        rom_name = os.path.basename(self.game['path'])

        self.log_status(f"검색 중: {rom_name}")
        self.log_status(f"시스템 ID: {self.system_id}")

        # Search game
        game_data = api.searchGame(rom_full_path, self.system_id, rom_name)

        if game_data is None:
            self.log_status("게임을 찾을 수 없습니다.")
            return

        # Display game info
        game_info = api.getGameInfo(game_data, lang='ko')
        self.log_status(f"\n=== 검색 결과 ===")
        self.log_status(f"게임 이름: {game_info.get('name', 'N/A')}")
        self.log_status(f"개발사: {game_info.get('developer', 'N/A')}")
        self.log_status(f"퍼블리셔: {game_info.get('publisher', 'N/A')}")
        self.log_status(f"장르: {game_info.get('genre', 'N/A')}")
        self.log_status(f"출시일: {game_info.get('releasedate', 'N/A')}")

        # Get image URLs
        images = api.getGameImages(game_data)
        self.log_status(f"\n=== 사용 가능한 이미지 ===")
        for img_type, url in images.items():
            self.log_status(f"  {img_type}: {url[:50]}...")

        # Download screenshot
        if 'ss' in images:
            image_dir = os.path.dirname(self.game['image'])
            if not image_dir:
                image_dir = './media/images'
            image_name = os.path.splitext(os.path.basename(self.game['path']))[0] + '.png'
            save_path = os.path.join(os.getcwd(), image_dir, image_name)

            self.log_status(f"\n이미지 다운로드 중: {save_path}")

            if api.downloadImage(images['ss'], save_path):
                self.log_status("이미지 다운로드 완료!")

                # Update XML
                if self.xml_manager:
                    self.game['image'] = os.path.join(image_dir, image_name).replace('\\', '/')
                    self.xml_manager.updateGame(self.game['path'], self.game)
                    self.log_status("XML 업데이트 완료!")
            else:
                self.log_status("이미지 다운로드 실패")
        else:
            self.log_status("\n스크린샷 이미지가 없습니다.")

        # Download box art
        if 'box-2D' in images:
            image_dir = os.path.dirname(self.game['image']) if self.game['image'] else './media/images'
            box_name = os.path.splitext(os.path.basename(self.game['path']))[0] + '_box.png'
            box_path = os.path.join(os.getcwd(), image_dir, box_name)

            self.log_status(f"\n박스 아트 다운로드 중: {box_path}")
            if api.downloadImage(images['box-2D'], box_path):
                self.log_status("박스 아트 다운로드 완료!")

    def _do_scrap_info(self):
        """Search game info only (no image download)."""
        from screenScraper import ScreenScraperAPI

        api = ScreenScraperAPI()

        if not api.isConfigured():
            self.log_status("오류: ScreenScraper 계정이 설정되지 않았습니다.")
            return

        if self.system_id is None:
            self.log_status(f"오류: '{self.sub_rom_dir}' 시스템의 ID를 찾을 수 없습니다.")
            return

        rom_full_path = os.path.join(os.getcwd(), self.game['path'])
        rom_name = os.path.basename(self.game['path'])

        self.log_status(f"게임 정보 검색 중: {rom_name}")

        game_data = api.searchGame(rom_full_path, self.system_id, rom_name)

        if game_data is None:
            self.log_status("게임을 찾을 수 없습니다.")
            return

        game_info = api.getGameInfo(game_data, lang='ko')

        self.log_status(f"\n=== 게임 정보 ===")
        self.log_status(f"이름: {game_info.get('name', 'N/A')}")
        desc = game_info.get('description', 'N/A')
        if desc and len(desc) > 200:
            desc = desc[:200] + '...'
        self.log_status(f"설명: {desc}")
        self.log_status(f"개발사: {game_info.get('developer', 'N/A')}")
        self.log_status(f"퍼블리셔: {game_info.get('publisher', 'N/A')}")
        self.log_status(f"장르: {game_info.get('genre', 'N/A')}")

        # Ask to update game info
        result = QMessageBox.question(
            self,
            "정보 업데이트",
            "검색된 정보로 게임 정보를 업데이트하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes and self.xml_manager:
            if game_info.get('name'):
                self.game['name'] = game_info['name']
            if game_info.get('description'):
                self.game['desc'] = game_info['description']
            self.xml_manager.updateGame(self.game['path'], self.game)
            self.log_status("\n게임 정보가 업데이트되었습니다!")


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
