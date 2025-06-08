from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✉️ Оставить обращение")],
            [KeyboardButton(text="📜 Правила обращений")]
        ],
        resize_keyboard=True
    )

def appeal_type_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔒 Анонимно")],
            [KeyboardButton(text="📞 С обратной связью")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def write_appeal_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def category_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚨 Криминал")],
            [KeyboardButton(text="🏘️ Социальная проблема")],
            [KeyboardButton(text="📌 Прочее")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def back_to_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ В главное меню")]],
        resize_keyboard=True
    )

def admin_kb(message_ids: List[int], user_id: int) -> InlineKeyboardMarkup:
    if len(message_ids)==1:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🚔 Заблокировать", callback_data=f"action:block:{user_id}:{message_ids[0]}"),
                    InlineKeyboardButton(text="🚫 Игнорировать", callback_data=f"action:skip:{user_id}:{message_ids[0]}")
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🚔 Заблокировать", callback_data=f"action:block:{user_id}:{":".join(message_ids)}"),
                    InlineKeyboardButton(text="🚫 Игнорировать", callback_data=f"action:skip:{user_id}:{":".join(message_ids)}")
                ]
            ]
        )