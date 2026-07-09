from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

STYLES = {
    "original": "Как сказано",
    "formal": "Формальный",
    "friendly": "Дружелюбный",
    "summary": "Конспект",
}


def get_style_keyboard(
    current_style: str = "original", show_split: bool = True
) -> InlineKeyboardMarkup:
    def label(key: str) -> str:
        name = STYLES[key]
        return f"✓ {name}" if key == current_style else name

    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=label("original"), callback_data="style:original"),
            InlineKeyboardButton(text=label("formal"), callback_data="style:formal"),
        ],
        [
            InlineKeyboardButton(text=label("friendly"), callback_data="style:friendly"),
            InlineKeyboardButton(text=label("summary"), callback_data="style:summary"),
        ],
    ]

    if show_split:
        rows.append([
            InlineKeyboardButton(
                text="✂️ Разбить для Авито", callback_data="split:avito"
            ),
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)
