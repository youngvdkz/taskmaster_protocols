from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs


def protocols_keyboard(protocols: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"p:{protocol_id}")]
            for protocol_id, title in protocols
        ]
    )


def items_keyboard(items: list[tuple[int, str, bool]], protocol_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for item_id, title, checked in items:
        prefix = "✅" if checked else "\u2800"
        label = f"{prefix} {title}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"t:{protocol_id}:{item_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _with_user_id(url: str, user_id: int) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["user_id"] = [str(user_id)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def main_menu_keyboard(webapp_url: str, user_id: int) -> ReplyKeyboardMarkup:
    webapp_url = _with_user_id(webapp_url, user_id)
    buttons = [
        [KeyboardButton(text="Open Mini App", web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text="Protocols")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
