# ----------------------------------------------------------------------
# keyboards.py - ماژول نهایی کیبوردهای ربات
# ----------------------------------------------------------------------

from typing import Dict, List, Any, Optional

# --- توابع کمکی برای تولید دکمه ---
def create_button(text: str, callback_data: Optional[str] = None, url: Optional[str] = None) -> Dict[str, str]:
    """ایجاد یک شیء دکمه برای API تلگرام"""
    button: Dict[str, str] = {"text": text}
    if callback_data:
        button["callback_data"] = callback_data
    if url:
        button["url"] = url
    return button

def create_keyboard(rows: List[List[Dict[str, Any]]]) -> Dict[str, List[List[Dict[str, Any]]]]:
    """تولید شیء InlineKeyboardMarkup نهایی برای API تلگرام"""
    return {"inline_keyboard": rows}

# --- ۱. منوی اصلی (سطح ۱) ---
def main_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    keyboard = [
        [create_button("خدمات 🔮", callback_data='MAIN|SERVICES|0')],
        [create_button("فروشگاه 🛍️", callback_data='MAIN|SHOP|0')],
        [create_button("شبکه‌های اجتماعی 🌐", callback_data='MAIN|SOCIALS|0')],
        [create_button("درباره ما و راهنما 🧑‍💻", callback_data='MAIN|ABOUT|0')],
    ]
    return create_keyboard(keyboard)

# --- ۲. منوی خدمات (سطح ۲) ---
def services_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی خدمات اصلی."""
    keyboard = [
        [create_button("آسترولوژی 🪐", callback_data='SERVICES|ASTRO|0')],
        [create_button("علم اعداد (سجیل) 🔢", callback_data='SERVICES|SIGIL|0')],
        [create_button("سنگ شناسی 💎", callback_data='SERVICES|GEM|0')],
        [create_button("گیاه شناسی 🌿", callback_data='SERVICES|HERB|0')],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۳. منوی آسترولوژی (سطح ۳) ---
def astrology_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی اصلی آسترولوژی."""
    keyboard = [
        [create_button("چارت تولد (ناتال) 📝", callback_data='SERVICES|ASTRO|CHART_INPUT')],
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)

# --- ۴. منوی سنگ‌شناسی (سطح ۳) ---
def gem_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی اصلی سنگ‌شناسی."""
    keyboard = [
        [create_button("سنگ شخصی 🔮", callback_data='GEM|PERSONAL|0')],
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)
    
# --- ۵. کیبورد بازگشت به منوی اصلی ---
def back_to_main_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """یک کیبورد ساده با دکمه بازگشت به منوی اصلی."""
    keyboard = [
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۶. منوی ورود زمان (NEW) ---
def time_input_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """کیبورد اینلاین برای انتخاب زمان پیش‌فرض یا ورود دستی."""
    keyboard = [
        [
            create_button("نمی‌دانم / پیش‌فرض (12:00) 🕐", callback_data='TIME|DEFAULT|12:00'),
        ],
        [create_button("بازگشت به تاریخ 🔙", callback_data='SERVICES|ASTRO|CHART_INPUT')],
    ]
    return create_keyboard(keyboard)
