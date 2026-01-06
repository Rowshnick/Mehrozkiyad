from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def sajil_start_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✏️ شروع ثبت اعداد", callback_data="SAJIL|START"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="MAIN|BACK"),
    )
    return kb
