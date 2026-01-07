#====================================
#symbol_keyboards
#====================================
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# -----------------------------
# مرحله ۱: انتخاب هدف
# -----------------------------
def goal_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🎯 هدف ۱", callback_data="goal:1"),
        InlineKeyboardButton("🎯 هدف ۲", callback_data="goal:2"),
        InlineKeyboardButton("🎯 هدف ۳", callback_data="goal:3"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main"),
    )
    return kb


# -----------------------------
# مرحله ۲: انتخاب فرهنگ
# -----------------------------
def culture_keyboard(goal_id: str):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🌍 فرهنگ ایرانی", callback_data=f"culture:{goal_id}:iran"),
        InlineKeyboardButton("🌍 فرهنگ یونانی", callback_data=f"culture:{goal_id}:greek"),
        InlineKeyboardButton("🌍 فرهنگ مصری", callback_data=f"culture:{goal_id}:egypt"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="start_symbol"),
    )
    return kb


# -----------------------------
# مرحله ۳: انتخاب انرژی
# -----------------------------
def energy_keyboard(goal_id: str, culture_id: str):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("⚡ انرژی مثبت", callback_data=f"energy:{goal_id}:{culture_id}:positive"),
        InlineKeyboardButton("⚡ انرژی محافظ", callback_data=f"energy:{goal_id}:{culture_id}:protective"),
        InlineKeyboardButton("⚡ انرژی تحول", callback_data=f"energy:{goal_id}:{culture_id}:transform"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data=f"culture:{goal_id}"),
    )
    return kb


# -----------------------------
# مرحله ۴: انتخاب نماد نهایی
# -----------------------------
def symbol_keyboard(goal_id: str, culture_id: str, energy_id: str):
    kb = InlineKeyboardMarkup(row_width=1)

    # این بخش را می‌توانی بعداً با دیتابیس یا فایل نمادها پر کنی
    kb.add(
        InlineKeyboardButton("🔯 نماد ۱", callback_data=f"symbol:{goal_id}:{culture_id}:{energy_id}:1"),
        InlineKeyboardButton("🔯 نماد ۲", callback_data=f"symbol:{goal_id}:{culture_id}:{energy_id}:2"),
        InlineKeyboardButton("🔯 نماد ۳", callback_data=f"symbol:{goal_id}:{culture_id}:{energy_id}:3"),
    )

    kb.add(
        InlineKeyboardButton("⬅️ بازگشت", callback_data=f"energy:{goal_id}:{culture_id}")
    )

    return kb
