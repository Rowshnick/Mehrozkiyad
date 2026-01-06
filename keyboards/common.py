from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def time_input_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🕛 00:00", callback_data="TIME|DEFAULT|00:00"),
        InlineKeyboardButton("🕐 01:00", callback_data="TIME|DEFAULT|01:00"),
        InlineKeyboardButton("🕒 03:00", callback_data="TIME|DEFAULT|03:00"),
        InlineKeyboardButton("🕕 06:00", callback_data="TIME|DEFAULT|06:00"),
        InlineKeyboardButton("🕘 09:00", callback_data="TIME|DEFAULT|09:00"),
        InlineKeyboardButton("🕛 12:00", callback_data="TIME|DEFAULT|12:00"),
        InlineKeyboardButton("🕒 15:00", callback_data="TIME|DEFAULT|15:00"),
        InlineKeyboardButton("🕕 18:00", callback_data="TIME|DEFAULT|18:00"),
        InlineKeyboardButton("🕘 21:00", callback_data="TIME|DEFAULT|21:00"),
    )
    kb.add(
        InlineKeyboardButton("⏳ وارد کردن دستی", callback_data="TIME|MANUAL")
    )
    return kb
