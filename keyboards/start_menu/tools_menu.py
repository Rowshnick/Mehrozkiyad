#--------‐-------------------‐-----------
#tools_menu.py
#--------‐-------------------‐-----------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def tools_menu():
    kb = [
        [
            InlineKeyboardButton(text="🕒 تبدیل تاریخ", callback_data="tool_date_convert"),
        ],
        [
            InlineKeyboardButton(text="🌍 تبدیل منطقه زمانی", callback_data="tool_timezone"),
        ],
        [
            InlineKeyboardButton(text="🔢 محاسبه عدد مسیر زندگی", callback_data="tool_life_path"),
        ],
        [
            InlineKeyboardButton(text="⬅️ بازگشت", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
