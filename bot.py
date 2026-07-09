import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TELEGRAM_TOKEN, validate_config
from handlers import document, start, text, voice
from middlewares.auth import AuthMiddleware


async def main() -> None:
    validate_config()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.include_router(start.router)
    dp.include_router(document.router)
    dp.include_router(voice.router)
    dp.include_router(text.router)

    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
