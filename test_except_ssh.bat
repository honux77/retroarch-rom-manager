@echo off
echo Running tests excluding SSH...
python -m pytest -m "not requires_ssh"
pause
