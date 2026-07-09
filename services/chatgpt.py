import logging
import re

from prompts.styles import (
    AVITO_SPLIT_PROMPT,
    BASE_SYSTEM_PROMPT,
    STYLE_PROMPTS,
    STYLE_TEMPERATURES,
)
from services.openai_client import client

logger = logging.getLogger(__name__)


async def improve_text(text: str, style: str = "original") -> str:
    style_prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["original"])
    temperature = STYLE_TEMPERATURES.get(style, 0.5)
    system_prompt = BASE_SYSTEM_PROMPT + "\n\n" + style_prompt

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=temperature,
        max_tokens=2000,
    )

    result = response.choices[0].message.content
    if result is None:
        raise ValueError("ChatGPT вернул пустой ответ")
    return result.strip()


async def split_for_avito(text: str) -> list[str]:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AVITO_SPLIT_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content
    if raw is None:
        return [text]

    parts = re.split(r"---СООБЩЕНИЕ\s*\d*---", raw)
    messages = [p.strip() for p in parts if p.strip()]

    return messages if messages else [text]
