#---------‐-------------------‐-----------
# main_menu.py
#--------‐-------------------‐------------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_main_menu():
    kb = [
        [
            InlineKeyboardButton(text="🔮 تحلیل‌های نجومی", callback_data="menu_astrology"),
        ],
        [
            InlineKeyboardButton(text="✨ نمادشناسی", callback_data="menu_symbols"),
        ],
        [
            InlineKeyboardButton(text="🧿 سجیل شخصی", callback_data="menu_sajil"),
        ],
        [
            InlineKeyboardButton(text="⚙️ ابزارها", callback_data="menu_tools"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_to_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ بازگشت به منوی اصلی", callback_data="back_main")]
        ]
    )
