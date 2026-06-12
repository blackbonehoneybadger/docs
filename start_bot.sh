#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Запускаю Badger CFO бота... Не закрывай это окно."
python3 -m app.telegram.bot
