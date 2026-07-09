from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

WELCOME_TEXT = (
    "Привет! Отправь мне текст или голосовое — я улучшу его.\n\n"
    "Режимы:\n"
    "• Как сказано — чищу текст, сохраняя стиль\n"
    "• Формальный — деловой тон\n"
    "• Дружелюбный — лёгкий стиль\n"
    "• Конспект — структурированная выжимка\n\n"
    "По умолчанию работаю в режиме «Как сказано». "
    "Стиль можно сменить кнопками после ответа."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)
