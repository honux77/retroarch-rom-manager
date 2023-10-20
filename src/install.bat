pyinstaller -F --name="RetroArch Rom Manager" --icon="./resources/gamepad.ico" \
--add-data "config.json;config.json" --add-data "resources;resources"  --add-data "secret.ini:secret.init"
main.py