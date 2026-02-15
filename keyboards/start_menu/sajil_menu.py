#--------‐-------------------‐-----------
#sajil_menu.py
#--------‐-------------------‐-----------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def sajil_menu():
    kb = [
        [
            InlineKeyboardButton(text="🧿 محاسبهٔ سجیل جدید", callback_data="start_sajil"),
        ],
        [
            InlineKeyboardButton(text="📘 مشاهدهٔ گزارش قبلی", callback_data="sajil_last_report"),
        ],
        [
            InlineKeyboardButton(text="⬅️ بازگشت", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
