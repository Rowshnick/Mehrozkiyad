from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def transits_main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔮 کلی", callback_data="menu_general"),
        InlineKeyboardButton("💞 عشق", callback_data="menu_love"),
        InlineKeyboardButton("🜂 کارما", callback_data="menu_karmic"),
        InlineKeyboardButton("💼 شغل", callback_data="menu_job"),
        InlineKeyboardButton("⚠️ چالش", callback_data="menu_challenge"),
    )
    return kb


def submenu_general():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔮 ۳۰ روز آینده", callback_data="general_30"),
        InlineKeyboardButton("🔮 امروز", callback_data="general_today"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_main"),
    )
    return kb


def submenu_love():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💞 ۳۰ روز آینده", callback_data="love_30"),
        InlineKeyboardButton("💞 امروز", callback_data="love_today"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_main"),
    )
    return kb


def submenu_karmic():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🜂 ۳۰ روز آینده", callback_data="karmic_30"),
        InlineKeyboardButton("🜂 امروز", callback_data="karmic_today"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_main"),
    )
    return kb


def submenu_job():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💼 ۳۰ روز آینده", callback_data="job_30"),
        InlineKeyboardButton("💼 امروز", callback_data="job_today"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_main"),
    )
    return kb


def submenu_challenge():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("⚠️ ۳۰ روز آینده", callback_data="challenge_30"),
        InlineKeyboardButton("⚠️ امروز", callback_data="challenge_today"),
        InlineKeyboardButton("⬅️ بازگشت", callback_data="back_to_main"),
    )
    return kb
