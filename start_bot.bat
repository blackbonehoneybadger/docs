@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запускаю Badger CFO бота... Не закрывай это окно.
python -m app.telegram.bot
echo.
echo Бот остановлен.
pause
