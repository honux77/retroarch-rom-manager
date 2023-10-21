pyinstaller -F --name="RetroArch Rom Manager" --icon="./resources/gamepad.ico" --add-data "config.json;config.json" --add-data "resources;resources"  --add-data "secret.ini:secret.ini" main.py
copy config.json dist\config.json
copy secret.ini dist\secret.ini
md dist\resources
copy resources dist\resources
