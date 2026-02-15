#--------‐-------------------‐-----------
#symbol_menu.py
#--------‐-------------------‐-----------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def symbol_main_menu():
    kb = [
        [
            InlineKeyboardButton(text="❤️ عشق", callback_data="symbol_goal_love"),
            InlineKeyboardButton(text="💰 ثروت", callback_data="symbol_goal_money"),
        ],
        [
            InlineKeyboardButton(text="🛡 محافظت", callback_data="symbol_goal_protection"),
            InlineKeyboardButton(text="🔥 انرژی", callback_data="symbol_goal_energy"),
        ],
        [
            InlineKeyboardButton(text="⬅️ بازگشت", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
