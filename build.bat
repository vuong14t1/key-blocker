@echo off
echo ========================================
echo    KEY BLOCKER - BUILD SCRIPT
echo ========================================
echo.

echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
)

echo.
echo [2/4] Checking keyboard module...
pip show keyboard >nul 2>&1
if errorlevel 1 (
    echo keyboard module is not installed. Installing...
    pip install keyboard
)

echo.
echo [3/4] Removing old build directories (if any)...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [4/4] Building .exe...
python -m PyInstaller --clean KeyBlocker.spec

echo.
echo ========================================
if exist "dist\KeyBlocker.exe" (
    echo BUILD SUCCEEDED!
    echo .exe location: dist\KeyBlocker.exe
    echo.
    echo You can:
    echo - Run directly: dist\KeyBlocker.exe
    echo - Create a Desktop shortcut
    echo - Move the file anywhere you like
) else (
    echo BUILD FAILED!
    echo Please check the errors above.
)
echo ========================================
echo.
pause
