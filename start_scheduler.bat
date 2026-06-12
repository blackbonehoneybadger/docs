@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запускаю планировщик отчётов (утро/вечер)... Не закрывай это окно.
python -m app.scheduler
pause
