from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import ALLOWED_USERS


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or user.id not in ALLOWED_USERS:
            if isinstance(event, Message):
                await event.answer(
                    "⛔ Доступ ограничен. Этот бот работает в приватном режиме."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⛔ Доступ ограничен.",
                    show_alert=True,
                )
            return None
        return await handler(event, data)
