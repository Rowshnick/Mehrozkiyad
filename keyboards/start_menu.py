from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔮 چارت تولد", callback_data="natal_chart")
            ],
            [
                InlineKeyboardButton(text="♓️ نمادها", callback_data="symbols")
            ],
            [
                InlineKeyboardButton(text="🪐 ترانزیت‌ها", callback_data="transits")
            ]
        ]
    )
