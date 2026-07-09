import logging
import os

import aiofiles
from aiogram import Bot, F, Router
from aiogram.types import Message

from handlers.state import save_text
from keyboards.inline import get_style_keyboard
from services.whisper import fix_transcription, transcribe_voice

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot) -> None:
    status = await message.reply("🎤 Распознаю голосовое...")

    tmp_path = f"/tmp/voice_{message.message_id}.ogg"

    try:
        file = await bot.get_file(message.voice.file_id)
        result = await bot.download_file(file.file_path)
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(result.read())

        try:
            raw_text = await transcribe_voice(tmp_path)
        except Exception:
            logger.exception("Ошибка транскрибации")
            await status.delete()
            await message.answer(
                "Не удалось распознать голосовое. "
                "Попробуйте записать ещё раз, говорите чётче."
            )
            return

        try:
            fixed_text = await fix_transcription(raw_text)
        except Exception:
            logger.exception("Ошибка пост-обработки транскрибации")
            fixed_text = raw_text

        await status.delete()

        sent = await message.answer(
            f"📝 Распознанный текст:\n\n{fixed_text}",
            reply_markup=get_style_keyboard("original", show_split=False),
        )
        save_text(sent.message_id, original=fixed_text)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
