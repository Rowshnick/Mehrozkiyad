# keyboards.py
# =============================================================================
# ماژول ساخت کیبوردهای اینلاین ربات
# -----------------------------------------------------------------------------
# این فایل تمام دکمه‌های مورد نیاز ربات را تولید می‌کند:
#   - منوی اصلی
#   - انتخاب خدمات
#   - انتخاب زمان پیش‌فرض
#   - بازگشت به منو
# =============================================================================

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# -----------------------------------------------------------------------------
# ۱) منوی اصلی
# -----------------------------------------------------------------------------

def main_menu_keyboard():
    """
    کیبورد اصلی ربات.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "🔮 آسترولوژی (چارت تولد)", "callback_data": "SERVICES|ASTRO|0"}
            ],
            [
                {"text": "📊 سرویس سجیل", "callback_data": "SERVICES|SAJIL|0"}
            ],
            [
                {"text": "ℹ️ درباره ما", "callback_data": "MAIN|ABOUT"}
            ]
        ]
    }


# -----------------------------------------------------------------------------
# ۲) انتخاب زمان پیش‌فرض
# -----------------------------------------------------------------------------

def time_input_keyboard():
    """
    کیبورد انتخاب زمان‌های رایج برای راحتی کاربر.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "🕛 00:00", "callback_data": "TIME|DEFAULT|00:00"},
                {"text": "🕐 01:00", "callback_data": "TIME|DEFAULT|01:00"},
                {"text": "🕒 03:00", "callback_data": "TIME|DEFAULT|03:00"},
            ],
            [
                {"text": "🕕 06:00", "callback_data": "TIME|DEFAULT|06:00"},
                {"text": "🕘 09:00", "callback_data": "TIME|DEFAULT|09:00"},
                {"text": "🕛 12:00", "callback_data": "TIME|DEFAULT|12:00"},
            ],
            [
                {"text": "🕒 15:00", "callback_data": "TIME|DEFAULT|15:00"},
                {"text": "🕕 18:00", "callback_data": "TIME|DEFAULT|18:00"},
                {"text": "🕘 21:00", "callback_data": "TIME|DEFAULT|21:00"},
            ],
            [
                {"text": "⏳ وارد کردن دستی", "callback_data": "TIME|MANUAL"}
            ]
        ]
    }


# -----------------------------------------------------------------------------
# ۳) کیبورد بازگشت به منوی اصلی
# -----------------------------------------------------------------------------

def back_to_main_keyboard():
    """
    دکمه بازگشت به منوی اصلی.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "🔙 بازگشت به منوی اصلی", "callback_data": "MAIN|BACK"}
            ]
        ]
    }


# -----------------------------------------------------------------------------
# ۴) کیبورد مخصوص سرویس سجیل
# -----------------------------------------------------------------------------

def sajil_start_keyboard():
    """
    کیبورد شروع سرویس سجیل.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "✏️ شروع ثبت اعداد", "callback_data": "SAJIL|START"}
            ],
            [
                {"text": "🔙 بازگشت", "callback_data": "MAIN|BACK"}
            ]
        ]
    }
# =========================
#   منوی اصلی ترانزیت‌ها
# =========================

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


# =========================
#   زیرمنوهای دسته‌بندی
# =========================

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

