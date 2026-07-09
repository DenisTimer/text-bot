import logging
from pathlib import Path

from services.openai_client import client

logger = logging.getLogger(__name__)


async def transcribe_voice(file_path: str) -> str:
    path = Path(file_path)
    with open(path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru",
            prompt="Расшифровка голосового сообщения на русском языке. Контекст: деловое и бытовое общение.",
        )

    text = response.text.strip()
    if not text:
        raise ValueError("Whisper не вернул текст")
    return text


async def fix_transcription(text: str) -> str:
    """Исправляет ошибки транскрибации через ChatGPT."""
    response = await client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты редактор разговорного текста. Тебе дают сырую речь — голосовое "
                    "сообщение, расшифровку с ошибками, слова-паразиты, обрывки мыслей, "
                    "опечатки распознавания.\n\n"
                    "Твоя задача:\n\n"
                    "— Восстанови смысл, даже если текст сбивчивый или неразборчивый\n"
                    "— Убери слова-паразиты («короче», «вот», «как-то», «как будто все», "
                    "«ну», «типа»)\n"
                    "— Исправь ошибки распознавания речи («павел катеринару» → "
                    "«повёл к ветеринару»)\n"
                    "— Сохрани живой разговорный стиль — не превращай в официальный текст\n"
                    "— Сохрани структуру и хронологию событий\n"
                    "— Если что-то совсем неразборчиво — восстанови по контексту\n"
                    "— Имена собственные уточняй по контексту\n"
                    "— Раздели на абзацы по смыслу\n\n"
                    "Верни ТОЛЬКО готовый текст, без пояснений."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_completion_tokens=4000,
    )

    result = response.choices[0].message.content
    if result is None:
        return text
    return result.strip()
