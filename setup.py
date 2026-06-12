"""Badger CFO: интерактивная установка для новичка.

Запуск:  python setup.py   (или двойной клик по install.bat на Windows)

Делает всё сам:
1. Ставит зависимости.
2. Создаёт .env из .env.example.
3. Генерирует ключ шифрования FERNET_KEY.
4. Спрашивает токен Telegram-бота и проверяет его через Telegram API.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

TOKEN_RE = re.compile(r"^\d{6,12}:[A-Za-z0-9_-]{30,}$")


def step(msg: str) -> None:
    print(f"\n=== {msg} ===")


def install_requirements() -> None:
    step("Шаг 1/4: установка зависимостей (1-3 минуты)")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")]
    )
    # Доверяем не коду возврата pip, а тому, что модули реально импортируются.
    missing = []
    for module in ("fastapi", "uvicorn", "sqlalchemy", "httpx", "cryptography",
                   "reportlab", "PIL", "pydantic_settings"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        print(f"ОШИБКА: не установились модули: {', '.join(missing)}.")
        print("Проверь интернет и запусти установку ещё раз.")
        sys.exit(1)
    print("Зависимости установлены.")


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    source = ENV_FILE if ENV_FILE.exists() else ENV_EXAMPLE
    for line in source.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def save_env(values: dict[str, str]) -> None:
    # Keep the example's layout/comments, only substitute values.
    lines = []
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key = line.partition("=")[0].strip()
            lines.append(f"{key}={values.get(key, '')}")
        else:
            lines.append(line)
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_fernet_key(values: dict[str, str]) -> None:
    step("Шаг 2/4: ключ шифрования")
    if values.get("FERNET_KEY"):
        print("FERNET_KEY уже есть — оставляю как есть.")
        return
    from cryptography.fernet import Fernet

    values["FERNET_KEY"] = Fernet.generate_key().decode()
    print("Ключ шифрования сгенерирован.")


def check_token(token: str) -> str | None:
    """Возвращает username бота, если токен рабочий."""
    try:
        import httpx

        resp = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = resp.json()
        if data.get("ok"):
            return data["result"].get("username", "?")
    except Exception:
        pass
    return None


def ensure_telegram_token(values: dict[str, str]) -> None:
    step("Шаг 3/4: токен Telegram-бота")
    current = values.get("TELEGRAM_BOT_TOKEN", "")
    if current:
        username = check_token(current)
        if username:
            print(f"Токен уже настроен, бот: @{username}")
            return
        print("Сохранённый токен не работает — введи новый.")

    print("Где взять токен: в Telegram найди @BotFather, отправь /newbot,")
    print("придумай имя и username — BotFather пришлёт токен вида 8123456789:AAGh7x...")
    while True:
        token = input("\nВставь токен сюда и нажми Enter (или Enter — пропустить): ").strip()
        if not token:
            print("Пропущено. Бот не заработает, пока не добавишь токен в .env.")
            return
        if not TOKEN_RE.match(token):
            print("Это не похоже на токен. Формат: цифры, двоеточие, длинная строка букв.")
            continue
        username = check_token(token)
        if username is None:
            print("Telegram не принял этот токен. Проверь, что скопировал целиком.")
            continue
        values["TELEGRAM_BOT_TOKEN"] = token
        print(f"Токен рабочий! Твой бот: @{username}")
        return


def main() -> None:
    print("Badger CFO — установка. Это займёт пару минут.")
    install_requirements()
    values = load_env()
    ensure_fernet_key(values)
    ensure_telegram_token(values)
    save_env(values)
    step("Шаг 4/4: готово")
    print("Настройки сохранены в файл .env")
    print("\nЧто дальше:")
    print("  Windows: двойной клик по start_bot.bat")
    print("  Mac/Linux: ./start_bot.sh")
    print("Потом напиши своему боту в Telegram: /help")


if __name__ == "__main__":
    main()
