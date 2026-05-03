@echo off
echo ========================================
echo    KEY BLOCKER - BUILD SCRIPT
echo ========================================
echo.

echo [1/4] Kiem tra PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller chua duoc cai dat. Dang cai dat...
    pip install pyinstaller
)

echo.
echo [2/4] Kiem tra keyboard module...
pip show keyboard >nul 2>&1
if errorlevel 1 (
    echo keyboard module chua duoc cai dat. Dang cai dat...
    pip install keyboard
)

echo.
echo [3/4] Xoa thu muc build cu (neu co)...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [4/4] Build file .exe...
python -m PyInstaller --clean KeyBlocker.spec

echo.
echo ========================================
if exist "dist\KeyBlocker.exe" (
    echo BUILD THANH CONG!
    echo File .exe tai: dist\KeyBlocker.exe
    echo.
    echo Ban co the:
    echo - Chay truc tiep: dist\KeyBlocker.exe
    echo - Tao shortcut tren Desktop
    echo - Chuyen file nay di bat ky dau
) else (
    echo BUILD THAT BAI!
    echo Vui long kiem tra loi o tren.
)
echo ========================================
echo.
pause
