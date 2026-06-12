@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo Python не найден!
    echo Установи его с https://python.org/downloads
    echo ВАЖНО: при установке поставь галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python setup.py
echo.
pause
