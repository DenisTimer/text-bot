import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.state import save_text, user_texts
from keyboards.inline import get_style_keyboard
from services.chatgpt import improve_text, split_for_avito

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    status = await message.reply("⏳ Обрабатываю...")

    try:
        result = await improve_text(message.text, style="original")
    except Exception:
        logger.exception("Ошибка при обработке текста")
        await status.delete()
        await message.answer("Ошибка обработки, попробуйте ещё раз")
        return

    await status.delete()
    sent = await message.answer(
        result, reply_markup=get_style_keyboard("original", show_split=True)
    )
    save_text(sent.message_id, original=message.text, improved=result)


@router.callback_query(F.data.startswith("style:"))
async def handle_style_callback(callback: CallbackQuery) -> None:
    style_id = callback.data.split(":")[1]
    logger.info(
        "CALLBACK style: message_id=%d, found=%s, keys=%s",
        callback.message.message_id,
        callback.message.message_id in user_texts,
        list(user_texts.keys()),
    )
    entry = user_texts.get(callback.message.message_id)

    if entry is None:
        await callback.answer("Текст не найден, отправьте заново", show_alert=True)
        return

    await callback.answer("⏳ Перегенерирую...")

    try:
        result = await improve_text(entry["original"], style=style_id)
    except Exception:
        logger.exception("Ошибка при перегенерации текста")
        await callback.answer(
            "Ошибка обработки, попробуйте ещё раз", show_alert=True
        )
        return

    entry["improved"] = result
    await callback.message.edit_text(
        result, reply_markup=get_style_keyboard(style_id, show_split=True)
    )


@router.callback_query(F.data == "split:avito")
async def handle_split_callback(callback: CallbackQuery) -> None:
    logger.info(
        "CALLBACK split: message_id=%d, found=%s",
        callback.message.message_id,
        callback.message.message_id in user_texts,
    )
    entry = user_texts.get(callback.message.message_id)

    if entry is None or entry["improved"] is None:
        await callback.answer("Текст не найден, отправьте заново", show_alert=True)
        return

    await callback.answer("✂️ Разбиваю на сообщения...")

    try:
        messages = await split_for_avito(entry["improved"])
    except Exception:
        logger.exception("Ошибка при разбивке текста")
        await callback.answer(
            "Ошибка разбивки, попробуйте ещё раз", show_alert=True
        )
        return

    total = len(messages)
    for i, text in enumerate(messages, start=1):
        await callback.message.answer(f"📨 Сообщение {i}/{total}:\n\n{text}")
