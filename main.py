# main.py
# RetroArch Rom Manager - PySide6 GUI Frontend

import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Local modules
import config as config_module
import LastStatus
import mainHandler
import fileUtil
import theme


def main():
    # Load config
    app_config = config_module.Config()
    mainHandler.initMainProgram(app_config)

    # Load last status
    status = LastStatus.LastStatus()

    # Store program path before changing directory
    program_path = os.getcwd()

    # Change working directory
    fileUtil.changeRootDir()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("RetroArch Rom Manager")

    # Apply theme
    theme.apply_theme(app)

    # Import MainWindow after app creation
    from ui.main_window import MainWindow

    # Create main window
    window = MainWindow(app_config, status)
    window.program_path = program_path

    # Read sub directories
    base_path = app_config.getBasePath()
    sub_dirs = fileUtil.readSubDirs()

    # Handle case when no sub ROM folders exist
    while len(sub_dirs) == 0:
        from ui.dialogs import show_error, get_directory

        show_error(None, "서브 롬 폴더 없음",
                   "기본 폴더에 서브 롬 폴더가 없습니다. 기본 폴더를 다시 선택해 주세요.")

        base_path = get_directory(None, "기본 폴더 선택", app_config.getBasePath())
        if not base_path:
            sys.exit(1)

        os.chdir(base_path)
        sub_dirs = fileUtil.readSubDirs()

        # Update config
        app_config.setBasePath(base_path)

    # Initialize ROM folders and show window
    window.init_rom_folders(sub_dirs)
    window.show()

    # Trigger initial ROM list load
    if window.sub_rom_dir_combo.currentText():
        window._on_rom_dir_changed(window.sub_rom_dir_combo.currentText())

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
