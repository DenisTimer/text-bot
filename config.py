import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

_raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = {
    int(uid.strip()) for uid in _raw_users.split(",") if uid.strip()
}


def validate_config() -> None:
    missing: list[str] = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        print(
            f"Ошибка: не заданы переменные окружения: {', '.join(missing)}\n"
            "Создайте файл .env по образцу .env.example",
            file=sys.stderr,
        )
        sys.exit(1)
    if not ALLOWED_USERS:
        print(
            "Предупреждение: ALLOWED_USERS не задан — бот не будет отвечать никому",
            file=sys.stderr,
        )
