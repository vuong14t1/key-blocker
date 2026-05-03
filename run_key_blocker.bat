@echo off
chcp 65001 >nul
title Key Blocker

echo ========================================
echo    KEY BLOCKER - KEY BLOCKING TOOL
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check the keyboard library
python -c "import keyboard" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing the keyboard library...
    pip install keyboard
    if errorlevel 1 (
        echo [ERROR] Failed to install the keyboard library
        pause
        exit /b 1
    )
)

:: Run the program with admin privileges
echo [INFO] Starting the program...
echo.
powershell -Command "Start-Process python -ArgumentList 'key_blocker.py' -Verb RunAs"

exit /b 0
