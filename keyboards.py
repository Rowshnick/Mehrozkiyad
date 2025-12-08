# ----------------------------------------------------------------------
# ماژول Keyboards - شامل توابعی برای تولید کیبوردهای اینلاین تلگرام.
# ----------------------------------------------------------------------

from typing import Dict, List, Any, Optional

# --- توابع کمکی برای تولید دکمه ---\
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
    keyboard = [
        [
            create_button("چارت آسترولوژی 🪐", callback_data='SERVICES|ASTRO|0'),
            create_button("سجیل 📜", callback_data='SERVICES|SIGIL|0'),
        ],
        [
            create_button("سنگ شخصی 💎", callback_data='SERVICES|GEM|0'),
            create_button("گیاه‌شناسی 🌿", callback_data='SERVICES|HERB|0'),
        ],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۳. منوی آسترولوژی (سطح ۳) ---
def astrology_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    keyboard = [
        [
            create_button("تولید چارت تولد 📝", callback_data='SERVICES|ASTRO|CHART_INPUT'),
        ],
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)


# --- ۴. منوی فروشگاه ---
def shop_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    keyboard = [
        [create_button("مشاوره چارت 📞", url="https://t.me/your_admin_link")],
        [create_button("سفارش سجیل شخصی ✨", url="https://t.me/your_admin_link")],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۵. منوی سنگ‌شناسی ---
def gem_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    keyboard = [
        [create_button("سنگ شخصی 💎", callback_data='GEM|PERSONAL_INPUT')],
        [create_button("اطلاعات سنگ‌ها 🔍", callback_data='GEM|INFO')],
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)

# --- ۶. منوی شبکه‌های اجتماعی ---
def socials_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    keyboard = [
        [
            create_button("کانال تلگرام", url="https://t.me/your_channel"),
            create_button("اینستاگرام", url="https://instagram.com/your_page"),
        ],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۷. دکمه بازگشت ساده ---
def back_to_main_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """یک کیبورد ساده با دکمه بازگشت به منوی اصلی."""
    keyboard = [
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۸. منوی چارت تولد (پس از محاسبه) - [جدید] ---
def birth_chart_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی کیبورد اینلاین برای نمایش نتایج چارت تولد."""
    keyboard = [
        [
            create_button("موقعیت سیارات 🪐", callback_data='CHART|PLANETS|0'),
            create_button("وضعیت خانه‌ها 🏡", callback_data='CHART|HOUSES|0'),
        ],
        [
            create_button("زوایای سیارات (Aspects) 📐", callback_data='CHART|ASPECTS|0'),
        ],
        [
            create_button("محاسبه دوباره 🔄", callback_data='SERVICES|ASTRO|CHART_INPUT'),
            create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0'),
        ]
    ]
    return create_keyboard(keyboard) 

# --- ۹. منوی جزئیات چارت (در دست ساخت) ---
def chart_menu_keyboard():
    """کیبورد اینلاین برای نمایش نتایج چارت (جزئیات، خانه‌ها، برگشت)"""
    
    # دکمه‌های اینلاین برای منوی چارت
    buttons = [
        [
            create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0'),
        ]
    ]
    return create_keyboard(buttons)
