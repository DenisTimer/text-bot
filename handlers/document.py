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

ALLOWED_AUDIO_MIMES = {
    "audio/ogg",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "video/webm",
    "application/ogg",
}

ALLOWED_EXTENSIONS = {".ogg", ".mp3", ".m4a", ".wav", ".webm", ".oga"}

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB — лимит Whisper API


def _is_audio_document(message: Message) -> bool:
    doc = message.document
    if doc is None:
        return False

    mime = doc.mime_type or ""
    if mime in ALLOWED_AUDIO_MIMES:
        return True

    file_name = doc.file_name or ""
    ext = os.path.splitext(file_name)[1].lower()
    return ext in ALLOWED_EXTENSIONS


async def _process_audio(message: Message, bot: Bot, file_id: str, ext: str) -> None:
    status = await message.reply("🎤 Распознаю аудио...")

    tmp_path = f"/tmp/doc_{message.message_id}{ext}"

    try:
        file = await bot.get_file(file_id)
        result = await bot.download_file(file.file_path)
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(result.read())

        try:
            raw_text = await transcribe_voice(tmp_path)
        except Exception:
            logger.exception("Ошибка транскрибации")
            await status.delete()
            await message.answer(
                "Не удалось распознать аудио. "
                "Попробуйте отправить другой файл."
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


@router.message(F.document)
async def handle_document(message: Message, bot: Bot) -> None:
    if not _is_audio_document(message):
        return

    doc = message.document
    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await message.answer("Файл слишком большой (максимум 25 МБ)")
        return

    file_name = doc.file_name or "audio.ogg"
    ext = os.path.splitext(file_name)[1] or ".ogg"

    await _process_audio(message, bot, doc.file_id, ext)


@router.message(F.audio)
async def handle_audio(message: Message, bot: Bot) -> None:
    audio = message.audio

    if audio.file_size and audio.file_size > MAX_FILE_SIZE:
        await message.answer("Файл слишком большой (максимум 25 МБ)")
        return

    file_name = audio.file_name or "audio.mp3"
    ext = os.path.splitext(file_name)[1] or ".mp3"

    await _process_audio(message, bot, audio.file_id, ext)
