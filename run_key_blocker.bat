@echo off
chcp 65001 >nul
title Key Blocker - Chan Phim

echo ========================================
echo    KEY BLOCKER - PHAN MEM CHAN PHIM
echo ========================================
echo.

:: Kiem tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Chua cai dat Python!
    echo Vui long tai Python tai: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Kiem tra thu vien keyboard
python -c "import keyboard" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dang cai dat thu vien keyboard...
    pip install keyboard
    if errorlevel 1 (
        echo [LOI] Khong the cai dat thu vien keyboard
        pause
        exit /b 1
    )
)

:: Chay chuong trinh voi quyen admin
echo [INFO] Dang khoi dong chuong trinh...
echo.
powershell -Command "Start-Process python -ArgumentList 'key_blocker.py' -Verb RunAs"

exit /b 0
