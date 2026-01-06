from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔮 گزارش ناتال", callback_data="start_natal"),
        InlineKeyboardButton("📜 ترانزیت‌ها", callback_data="start_transits"),
        InlineKeyboardButton("✨ Symbol Menu", callback_data="start_symbol"),
    )
    return kb


def back_to_main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_main")
    )
    return kb
