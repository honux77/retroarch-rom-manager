@echo off
echo === RetroArch Rom Manager 빌드 시작 ===

if exist build rd /s /q build
if exist dist rd /s /q dist

python -m PyInstaller -y "RetroArch Rom Manager.spec"
if errorlevel 1 (
    echo [오류] PyInstaller 빌드 실패
    pause
    exit /b 1
)

set "DEST=dist\RetroArch Rom Manager"

rem config.json은 spec에서 번들되지만 사용자가 수정할 수 있도록 별도 복사
copy /Y config.json "%DEST%\config.json"

rem secret.ini가 있으면 복사 (없으면 첫 실행 시 생성)
if exist secret.ini (
    copy /Y secret.ini "%DEST%\secret.ini"
) else (
    echo [경고] secret.ini 없음 - 배포본에 포함되지 않습니다.
)

echo.
echo === 빌드 완료: %DEST% ===
pause
