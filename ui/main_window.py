# ui/main_window.py
# Main window class for RetroArch Rom Manager

import os
import asyncio
from os import path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QListWidget, QListWidgetItem,
    QFrame, QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor

from .widgets import (
    StyledButton, ImagePreview, SectionLabel, TitleLabel, CardFrame,
    MissingImageListItem
)
from .dialogs import (
    GroovySyncDialog, ImageScrapDialog,
    show_error, show_info, ask_question, get_directory
)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config, status):
        super().__init__()
        self.config = config
        self.status = status
        self.last_rom_idx = status.getLastRomIdx()
        self.last_sub_rom_dir = status.getLastSubRomDirectory()
        self.program_path = os.getcwd()

        # XML Manager will be set after rom dir selection
        self.xml_manager = None

        self._setup_window()
        self._setup_ui()
        self._connect_signals()

    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("RetroArch Rom Manager v20251211")
        self.setMinimumSize(1200, 800)

        # Set window icon
        icon_path = os.path.join(self.program_path, "resources", "icon16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _setup_ui(self):
        """Setup the main UI layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Title section
        self._create_title_section(main_layout)

        # Content grid (3x2)
        content_layout = QGridLayout()
        content_layout.setSpacing(10)

        # Row 1: Rom list, Image preview, Action buttons
        self._create_rom_list_section(content_layout, 0, 0)
        self._create_image_preview_section(content_layout, 0, 1)
        self._create_action_buttons_section(content_layout, 0, 2)

        # Row 2: Output messages, Rom details, Settings
        self._create_output_section(content_layout, 1, 0)
        self._create_rom_details_section(content_layout, 1, 1)
        self._create_settings_section(content_layout, 1, 2)

        # Set column stretch
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 2)
        content_layout.setColumnStretch(2, 0)

        # Set row stretch
        content_layout.setRowStretch(0, 1)
        content_layout.setRowStretch(1, 1)

        main_layout.addLayout(content_layout)

        # Load default image
        self._load_default_image()

    def _create_title_section(self, parent_layout):
        """Create title and folder selection section."""
        title_frame = CardFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setSpacing(10)

        # App title
        title_label = TitleLabel("RetroArch Rom Manager")
        title_layout.addWidget(title_label)

        # Folder selection row
        folder_row = QHBoxLayout()
        folder_row.addStretch()

        folder_label = QLabel("롬 폴더:")
        folder_row.addWidget(folder_label)

        self.sub_rom_dir_combo = QComboBox()
        self.sub_rom_dir_combo.setMinimumWidth(250)
        folder_row.addWidget(self.sub_rom_dir_combo)

        self.refresh_button = StyledButton("새로고침", "default")
        self.refresh_button.setFixedWidth(100)
        folder_row.addWidget(self.refresh_button)

        folder_row.addStretch()
        title_layout.addLayout(folder_row)

        parent_layout.addWidget(title_frame)

    def _create_rom_list_section(self, layout, row, col):
        """Create ROM list section."""
        frame = CardFrame()
        frame_layout = QVBoxLayout(frame)

        # Section title
        title = SectionLabel("롬 리스트")
        frame_layout.addWidget(title)

        # List widget
        self.rom_list_widget = QListWidget()
        self.rom_list_widget.setMinimumWidth(300)
        frame_layout.addWidget(self.rom_list_widget)

        layout.addWidget(frame, row, col)

    def _create_image_preview_section(self, layout, row, col):
        """Create image preview section."""
        self.image_preview = ImagePreview()
        layout.addWidget(self.image_preview, row, col)

    def _create_action_buttons_section(self, layout, row, col):
        """Create action buttons section."""
        frame = CardFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)

        # Button width
        btn_width = 160

        # Section: Basic actions
        title = SectionLabel("기본 동작")
        frame_layout.addWidget(title)

        self.run_rom_button = StyledButton("선택 롬 실행", "green")
        self.run_rom_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.run_rom_button)

        self.open_rom_folder_button = StyledButton("롬 폴더 열기", "default")
        self.open_rom_folder_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.open_rom_folder_button)

        self.open_image_folder_button = StyledButton("이미지 폴더 열기", "default")
        self.open_image_folder_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.open_image_folder_button)

        self.image_scrap_button = StyledButton("이미지 스크랩", "blue")
        self.image_scrap_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.image_scrap_button)

        self.delete_rom_button = StyledButton("선택 롬/이미지 삭제", "red")
        self.delete_rom_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.delete_rom_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        frame_layout.addWidget(separator)

        # Section: Groovy sync
        groovy_title = SectionLabel("그루비 동기화")
        frame_layout.addWidget(groovy_title)

        self.export_list_button = StyledButton("리스트 내보내기", "default")
        self.export_list_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.export_list_button)

        self.sync_roms_button = StyledButton("롬 동기화", "green")
        self.sync_roms_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.sync_roms_button)

        frame_layout.addStretch()
        layout.addWidget(frame, row, col)

    def _create_output_section(self, layout, row, col):
        """Create output message section."""
        frame = CardFrame()
        frame_layout = QVBoxLayout(frame)

        # Section title
        title = SectionLabel("출력 메시지")
        frame_layout.addWidget(title)

        # Text widget
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        frame_layout.addWidget(self.output_text)

        layout.addWidget(frame, row, col)

    def _create_rom_details_section(self, layout, row, col):
        """Create ROM details section."""
        frame = CardFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)

        # Section title
        title = SectionLabel("롬 세부 정보")
        frame_layout.addWidget(title)

        # Form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(6)

        # ROM name
        form_layout.addWidget(QLabel("롬 이름"), 0, 0, Qt.AlignRight)
        self.rom_title_entry = QLineEdit()
        form_layout.addWidget(self.rom_title_entry, 0, 1)

        # ROM path
        form_layout.addWidget(QLabel("롬 경로"), 1, 0, Qt.AlignRight)
        self.rom_path_entry = QLineEdit()
        form_layout.addWidget(self.rom_path_entry, 1, 1)

        # Image path
        form_layout.addWidget(QLabel("이미지 경로"), 2, 0, Qt.AlignRight)
        self.rom_image_entry = QLineEdit()
        form_layout.addWidget(self.rom_image_entry, 2, 1)

        # Rating
        form_layout.addWidget(QLabel("Rating"), 3, 0, Qt.AlignRight)
        self.rom_rating_entry = QLineEdit()
        form_layout.addWidget(self.rom_rating_entry, 3, 1)

        # Description
        form_layout.addWidget(QLabel("세부 정보"), 4, 0, Qt.AlignRight | Qt.AlignTop)
        self.rom_description_text = QTextEdit()
        self.rom_description_text.setMaximumHeight(100)
        form_layout.addWidget(self.rom_description_text, 4, 1)

        frame_layout.addLayout(form_layout)

        # Buttons
        button_row = QHBoxLayout()

        self.update_rom_button = StyledButton("롬 정보 업데이트", "blue")
        button_row.addWidget(self.update_rom_button)

        self.translate_button = StyledButton("롬 정보 번역하기", "yellow")
        button_row.addWidget(self.translate_button)

        button_row.addStretch()
        frame_layout.addLayout(button_row)

        layout.addWidget(frame, row, col)

    def _create_settings_section(self, layout, row, col):
        """Create settings section."""
        frame = CardFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)

        btn_width = 160

        # Section title
        title = SectionLabel("설정")
        frame_layout.addWidget(title)

        self.set_base_path_button = StyledButton("기본 폴더 재설정", "default")
        self.set_base_path_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.set_base_path_button)

        self.set_target_path_button = StyledButton("기기 폴더 재설정", "default")
        self.set_target_path_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.set_target_path_button)

        self.open_config_button = StyledButton("설정 파일 열기", "default")
        self.open_config_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.open_config_button)

        self.open_retroarch_button = StyledButton("RetroArch 폴더 열기", "default")
        self.open_retroarch_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.open_retroarch_button)

        self.run_scrapper_button = StyledButton("Scrapper 실행", "green")
        self.run_scrapper_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.run_scrapper_button)

        self.delete_scrap_xml_button = StyledButton("ScrapXML 삭제", "red")
        self.delete_scrap_xml_button.setFixedWidth(btn_width)
        frame_layout.addWidget(self.delete_scrap_xml_button)

        frame_layout.addStretch()
        layout.addWidget(frame, row, col)

    def _load_default_image(self):
        """Load and set default preview image."""
        base_image_path = os.path.join(self.program_path, "resources", "base.png")
        if os.path.exists(base_image_path):
            pixmap = QPixmap(base_image_path)
            self.image_preview.set_default_image(pixmap)

    def _connect_signals(self):
        """Connect all UI signals to handlers."""
        # Combo box
        self.sub_rom_dir_combo.currentTextChanged.connect(self._on_rom_dir_changed)
        self.refresh_button.clicked.connect(self._refresh_rom_list)

        # ROM list
        self.rom_list_widget.currentRowChanged.connect(self._on_rom_selected)

        # Action buttons
        self.run_rom_button.clicked.connect(self._run_rom)
        self.open_rom_folder_button.clicked.connect(self._open_rom_folder)
        self.open_image_folder_button.clicked.connect(self._open_image_folder)
        self.image_scrap_button.clicked.connect(self._open_image_scrap)
        self.delete_rom_button.clicked.connect(self._delete_rom)

        # Groovy buttons
        self.export_list_button.clicked.connect(self._export_groovy_list)
        self.sync_roms_button.clicked.connect(self._sync_roms_to_groovy)

        # ROM detail buttons
        self.update_rom_button.clicked.connect(self._update_rom_info)
        self.translate_button.clicked.connect(self._translate_rom_info)

        # Settings buttons
        self.set_base_path_button.clicked.connect(self._set_base_path)
        self.set_target_path_button.clicked.connect(self._set_target_path)
        self.open_config_button.clicked.connect(self._open_config)
        self.open_retroarch_button.clicked.connect(self._open_retroarch_folder)
        self.run_scrapper_button.clicked.connect(self._run_scrapper)
        self.delete_scrap_xml_button.clicked.connect(self._delete_scrap_xml)

    def init_rom_folders(self, sub_dirs: list):
        """Initialize ROM folder combo box."""
        self.sub_rom_dir_combo.clear()
        self.sub_rom_dir_combo.addItems(sub_dirs)

        # Set last selected folder
        last_dir = self.status.getLastSubRomDirectory()
        if last_dir in sub_dirs:
            self.sub_rom_dir_combo.setCurrentText(last_dir)
        elif sub_dirs:
            self.sub_rom_dir_combo.setCurrentIndex(0)

    # ==================== Event Handlers ====================

    @Slot(str)
    def _on_rom_dir_changed(self, rom_dir: str):
        """Handle ROM directory change."""
        if not rom_dir:
            return

        import fileUtil
        import xmlUtil
        import scrapper

        read_rom = True

        # Check if directory actually changed
        if rom_dir != self.last_sub_rom_dir:
            self.last_sub_rom_dir = rom_dir
            self.last_rom_idx = 0
            read_rom = False

        fileUtil.changeSubRomDir(rom_dir)
        self.xml_manager = xmlUtil.XmlManager()
        self.xml_manager.readGamesFromXml()

        if self.xml_manager.tree is None:
            show_error(self, "XML 파일 없음",
                       f"{rom_dir}에 XML 파일이 없습니다. 폴더를 확인하고 환경 설정을 다시 해 주세요.")
            return

        scrapper.updateXMLFromScrapper(dryRun=False)

        # Clear lists
        self.rom_list_widget.clear()
        self.output_text.clear()

        img_found = 0
        img_miss_count = 0

        for game in self.xml_manager.gameList:
            rom_name = game['name']
            item = QListWidgetItem(rom_name)

            if not os.path.isfile(game['image']):
                if img_miss_count == 0:
                    self.output_text.append("=== 존재하지 않는 이미지 목록 ===\n")

                # Set missing style
                MissingImageListItem.set_missing_style(item)
                self.output_text.append(game['image'])
                img_miss_count += 1
            else:
                img_found += 1

            self.rom_list_widget.addItem(item)

        # Show summary
        if img_miss_count == 0:
            self.output_text.append(f"총 {img_found}개의 롬의 모든 이미지가 정상적으로 존재합니다.")
        else:
            self.output_text.append(f"\n총 {img_found + img_miss_count}개의 롬 중 {img_miss_count}개의 이미지가 존재하지 않습니다.")

        # Select last ROM
        if read_rom and self.rom_list_widget.count() > self.last_rom_idx:
            self.rom_list_widget.setCurrentRow(self.last_rom_idx)

    def _refresh_rom_list(self):
        """Refresh ROM list."""
        current_dir = self.sub_rom_dir_combo.currentText()
        if current_dir:
            self._on_rom_dir_changed(current_dir)

    @Slot(int)
    def _on_rom_selected(self, idx: int):
        """Handle ROM selection."""
        if idx < 0 or self.xml_manager is None:
            return

        self.last_rom_idx = idx
        game = self.xml_manager.findGameByIdx(idx)
        if game is None:
            return

        image_path = game['image']
        print("롬파일 정보 읽기:", game['path'])

        # Show image preview
        import imgUtil
        pixmap = imgUtil.findImageAsPixmap(image_path)

        if pixmap and not pixmap.isNull():
            self.image_preview.set_image(pixmap)
        else:
            self.image_preview.clear_image()

        # Update ROM details
        self.rom_title_entry.setText(game.get('name', ''))
        self.rom_path_entry.setText(game.get('path', ''))
        self.rom_image_entry.setText(game.get('image', ''))
        self.rom_rating_entry.setText(game.get('rating', ''))
        self.rom_description_text.setPlainText(game.get('desc', ''))

    def _run_rom(self):
        """Run selected ROM in RetroArch."""
        if self.xml_manager is None:
            return

        import mainHandler
        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        if game:
            asyncio.run(mainHandler.runRetroarch(
                self.sub_rom_dir_combo.currentText(),
                game['path'],
                self.config
            ))

    def _open_rom_folder(self):
        """Open ROM folder in file explorer."""
        folder_path = os.getcwd()
        self._open_folder(folder_path)

    def _open_image_folder(self):
        """Open image folder in file explorer."""
        if self.xml_manager is None:
            return

        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        if game and game.get('image'):
            folder_path = path.join(os.getcwd(), path.dirname(game['image']))
            self._open_folder(folder_path)

    def _open_folder(self, folder_path: str):
        """Open folder in system file explorer."""
        if path.exists(folder_path) and path.isdir(folder_path):
            os.startfile(folder_path)
        else:
            show_error(self, "폴더 없음", f"{folder_path} 가 없습니다. 폴더를 확인해 주세요.")

    def _open_image_scrap(self):
        """Open image scrap dialog."""
        if self.xml_manager is None:
            return

        from screenScraper import getSystemId

        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        system_id = getSystemId(self.last_sub_rom_dir)

        dialog = ImageScrapDialog(game, system_id, self.last_sub_rom_dir, self)
        dialog.set_xml_manager(self.xml_manager)
        dialog.exec()

        # Refresh after scraping
        self._refresh_rom_list()

    def _delete_rom(self):
        """Delete selected ROM and images."""
        if self.xml_manager is None:
            return

        import fileUtil

        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        if not ask_question(self, "삭제 확인", f"'{game['name']}' 롬과 이미지를 삭제하시겠습니까?"):
            return

        fileUtil.deleteRomAndImages(game)
        self.xml_manager.remove(game)
        self.last_rom_idx = 0
        self._refresh_rom_list()

    def _export_groovy_list(self):
        """Export Groovy list."""
        import groovy
        from syncFile import SyncFile

        sync_file = SyncFile()
        sync_file.setServerInfo("groovy")
        status = sync_file.connectSSH()

        if not status:
            show_error(self, "SSH 연결 실패", "SSH 연결에 실패했습니다. 설정을 확인해 주세요.")
            return

        sync_file.copyRemoteList()
        match, total = groovy.exportGroovyList()
        sync_file.exportLocalList()

        show_info(self, "그루비 리스트 내보내기",
                  f"그루비 리스트 {match}개를 변환해서 {sync_file.remotePath}로 내보냈습니다.\n")

    def _sync_roms_to_groovy(self):
        """Sync ROMs to Groovy server."""
        import time
        from syncFile import SyncFile

        sync_file = SyncFile()
        sync_file.setServerInfo("groovy")

        # Show sync dialog
        dialog = GroovySyncDialog(self)
        dialog.show()

        status = sync_file.connectSSH()
        if not status:
            dialog.close()
            show_error(self, "SSH 연결 실패", "SSH 연결에 실패했습니다. 설정을 확인해 주세요.")
            return

        dialog.set_status("그루비 서버에 접속 성공.")
        QApplication.processEvents()
        time.sleep(1)

        dialog.set_status(f"그루비와 {self.last_sub_rom_dir} 동기화 중...")

        def update_progress(current, total):
            if total > 0:
                dialog.set_progress(int(current / total * 100))
            dialog.set_status(f"동기화 중... ({current}/{total})")
            QApplication.processEvents()

        sync_status = sync_file.syncSubRoms(self.last_sub_rom_dir, callback=update_progress)

        dialog.finish_success()
        time.sleep(1)
        dialog.close()

        show_info(self, "그루비 리스트 내보내기",
                  f"{self.last_sub_rom_dir} 폴더의 롬 {sync_status[2]}개를 복사했습니다.\n")

    def _update_rom_info(self):
        """Update ROM information."""
        if self.xml_manager is None:
            return

        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        old_path = game['path']

        rom_info = f'''롬 이름: {self.rom_title_entry.text()}
롬 경로: {self.rom_path_entry.text()}
롬 Rating: {self.rom_rating_entry.text()}
이미지 경로: {self.rom_image_entry.text()}
세부 정보: {self.rom_description_text.toPlainText()[:100]}...'''

        if not ask_question(self, "롬 정보 업데이트", f"롬 정보를 업데이트 하시겠습니까?\n\n{rom_info}"):
            return

        game['name'] = self.rom_title_entry.text()
        game['path'] = self.rom_path_entry.text()
        game['rating'] = self.rom_rating_entry.text()
        game['image'] = self.rom_image_entry.text()
        game['desc'] = self.rom_description_text.toPlainText()

        self.last_rom_idx = self.xml_manager.updateGame(old_path, game)
        print("인덱스 업데이트:", self.last_rom_idx)
        self._refresh_rom_list()

    def _translate_rom_info(self):
        """Translate ROM information."""
        if self.xml_manager is None:
            return

        import translate

        game = self.xml_manager.findGameByIdx(self.last_rom_idx)
        filename = game['path']

        translate.translateGameInfo(game)

        self.rom_title_entry.setText(game['name'])
        self.rom_description_text.setPlainText(game['desc'])

        self.last_rom_idx = self.xml_manager.updateGame(filename, game)
        print("인덱스 업데이트:", self.last_rom_idx)
        self._refresh_rom_list()

    def _set_base_path(self):
        """Set base ROM folder path."""
        import fileUtil

        sub_dirs = []
        while True:
            base_path = get_directory(self, "기본 폴더 선택", self.config.getBasePath())
            if not base_path:
                return

            os.chdir(base_path)
            sub_dirs = fileUtil.readSubDirs()
            if len(sub_dirs) != 0:
                break
            show_error(self, "서브 롬 폴더 없음", "서브 롬 폴더가 없습니다. 폴더를 다시 선택해 주세요.")

        self.config.setBasePath(base_path)
        self.config.setLastRomDir(sub_dirs[0])
        self.config.save()

        self.sub_rom_dir_combo.clear()
        self.sub_rom_dir_combo.addItems(sub_dirs)
        self.sub_rom_dir_combo.setCurrentIndex(0)

    def _set_target_path(self):
        """Set target device folder path."""
        target_path = get_directory(self, "기기 폴더 선택", self.config.getTargetPath())
        if target_path:
            self.config.setTargetPath(target_path)
            self.config.save()

    def _open_config(self):
        """Open config file."""
        os.startfile(self.config.getConfigFilePath())

    def _open_retroarch_folder(self):
        """Open RetroArch folder."""
        retroarch_path = path.dirname(self.config.getRetroarchPath())
        self._open_folder(retroarch_path)

    def _run_scrapper(self):
        """Run external scrapper tool."""
        import mainHandler
        asyncio.run(mainHandler.runScrapper(self.config))

    def _delete_scrap_xml(self):
        """Delete ScrapXML file."""
        file_path = self.config.getScrapperXmlName()

        if not ask_question(self, "ScrapXML 삭제", f"ScrapXML 파일 {file_path}을 삭제하시겠습니까?"):
            return

        if path.isfile(file_path):
            os.remove(file_path)
            show_info(self, "ScrapXML 삭제", "ScrapXML 파일을 삭제했습니다.")
        else:
            show_info(self, "ScrapXML 삭제", "ScrapXML 파일이 없습니다.")

    def closeEvent(self, event):
        """Handle window close event."""
        print("메인 프로그램 종료")
        self.status.setLastRomIdx(self.last_rom_idx)
        self.status.setLastSubRomDirectory(self.sub_rom_dir_combo.currentText())
        self.status.save()
        event.accept()
