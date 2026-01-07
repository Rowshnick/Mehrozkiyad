from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔮 گزارش ناتال", callback_data="start_natal")],
            [InlineKeyboardButton(text="📜 ترانزیت‌ها", callback_data="start_transits")],
            [InlineKeyboardButton(text="✨ Symbol Menu", callback_data="start_symbol")],
        ]
    )


def back_to_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_main")]
        ]
    )
