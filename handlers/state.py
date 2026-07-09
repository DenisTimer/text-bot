import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

MAX_STORED_TEXTS = 100


class TextEntry(TypedDict):
    original: str
    improved: str | None


# message_id ответа бота → оригинальный и улучшенный текст
user_texts: dict[int, TextEntry] = {}


def save_text(message_id: int, original: str, improved: str | None = None) -> None:
    logger.info(
        "SAVE: message_id=%d, original_len=%d, improved=%s",
        message_id,
        len(original),
        "yes" if improved else "no",
    )
    user_texts[message_id] = {"original": original, "improved": improved}
    if len(user_texts) > MAX_STORED_TEXTS:
        oldest_keys = sorted(user_texts.keys())[: len(user_texts) - MAX_STORED_TEXTS]
        for key in oldest_keys:
            del user_texts[key]
    logger.info("SAVE: ключей в user_texts: %d", len(user_texts))
