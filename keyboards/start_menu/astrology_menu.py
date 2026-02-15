#--------‐-------------------‐-----------
# astrology_menu.py
#--------‐-------------------‐-----------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def astrology_menu():
    kb = [
        [
            InlineKeyboardButton(text="🌙 گزارش ناتال", callback_data="start_natal"),
        ],
        [
            InlineKeyboardButton(text="📜 ترانزیت‌های ۳۰ روز آینده", callback_data="start_transits"),
        ],
        [
            InlineKeyboardButton(text="♒ سازگاری نجومی", callback_data="start_compatibility"),
        ],
        [
            InlineKeyboardButton(text="⬅️ بازگشت", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
