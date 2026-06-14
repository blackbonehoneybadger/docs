#!/usr/bin/env bash
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
    echo "Python не найден! Установи с https://python.org/downloads"
    exit 1
fi
python3 setup.py
