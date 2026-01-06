from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_main_menu():
    kb = InlineKeyboardBuilder()

    kb.button(text="🔮 گزارش ناتال حرفه‌ای", callback_data="start_natal")
    kb.button(text="📜 ترانزیت‌ها", callback_data="start_transits")
    kb.button(text="✨ Symbol Menu", callback_data="start_symbol")

    kb.adjust(1)
    return kb.as_markup()
