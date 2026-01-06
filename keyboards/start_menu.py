from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_main_menu():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🔮 گزارش ناتال حرفه‌ای\n— چارت + تفسیر + PDF —",
        callback_data="start_natal"
    )
    kb.button(
        text="📜 ترانزیت‌ها\n— ۳۰ روز آینده + دسته‌بندی —",
        callback_data="start_transits"
    )
    kb.button(
        text="✨ Symbol Menu\n— انتخاب نماد انرژی —",
        callback_data="start_symbol"
    )

    kb.adjust(1)
    return kb.as_markup()


def back_to_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅ بازگشت به منوی اصلی", callback_data="back_main")
    return kb.as_markup()
