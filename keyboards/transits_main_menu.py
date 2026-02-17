#--------‐-------------------‐-----------
# keyboards/transits_main_menu.py
#--------‐-------------------‐-----------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def transits_main_menu():
    kb = [
        [
            InlineKeyboardButton(text="📅 ترانزیت ۳۰ روز آینده", callback_data="transits_30"),
        ],
        [
            InlineKeyboardButton(text="📅 ترانزیت امروز", callback_data="transits_today"),
        ],
        [
            InlineKeyboardButton(text="💞 ترانزیت‌های عاشقانه", callback_data="transits_love"),
        ],
        [
            InlineKeyboardButton(text="🜂 ترانزیت‌های کارمایی", callback_data="transits_karmic"),
        ],
        [
            InlineKeyboardButton(text="💼 ترانزیت‌های شغلی", callback_data="transits_job"),
        ],
        [
            InlineKeyboardButton(text="⚠️ ترانزیت‌های چالشی", callback_data="transits_challenge"),
        ],
        [
            InlineKeyboardButton(text="⬅️ بازگشت", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
