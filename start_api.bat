@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запускаю API-сервер (нужен для Plaid/бирж)... Не закрывай это окно.
echo Документация API: http://localhost:8000/docs
python -m uvicorn app.main:app
pause
