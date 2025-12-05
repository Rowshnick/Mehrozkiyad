# ----------------------------------------------------------------------
# ماژول Keyboards - شامل توابعی برای تولید کیبوردهای اینلاین تلگرام.
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
    """منوی خدمات: آسترولوژی، سنگ‌شناسی، نمادشناسی و گیاه شناسی."""
    keyboard = [
        [create_button("آسترولوژی 🔭", callback_data='SERVICES|ASTRO|0')],
        [create_button("سنگ شناسی 💎", callback_data='SERVICES|GEM|0')],
        [create_button("نماد شناسی (سجیل) ✨", callback_data='SERVICES|SIGIL|0')],
        [create_button("گیاه شناسی 🌿", callback_data='SERVICES|HERB|0')],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۳. منوی آسترولوژی (سطح ۳) ---
def astrology_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی آسترولوژی: تولید چارت و پیش‌گویی."""
    keyboard = [
        [create_button("تولید چارت تولد (زایچه) 📝", callback_data='SERVICES|ASTRO|CHART_INPUT')], 
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)

# --- ۴. منوی سنگ شناسی (سطح ۳) ---
def gem_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی سنگ‌شناسی با گزینه‌های متنوع."""
    keyboard = [
        [create_button("سنگ مناسب شخصی 👤", callback_data='GEM|PERSONAL_INPUT|0')], 
        [create_button("خواص هر سنگ 🔍", callback_data='GEM|INFO|0')],
        [create_button("بازگشت به خدمات ↩️", callback_data='MAIN|SERVICES|0')],
    ]
    return create_keyboard(keyboard)
    
# --- ۵. منوی فروشگاه (سطح ۲) ---
def shop_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی فروشگاه: سفارش خدمات."""
    keyboard = [
        [create_button("سفارش چارت تولد (کامل) 📄", callback_data='SHOP|ORDER|CHART')],
        [create_button("سفارش سنگ شخصی 💍", callback_data='SHOP|ORDER|GEM')],
        [create_button("پکیج کامل خدمات 🎁", callback_data='SHOP|ORDER|PACKAGE')],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۶. منوی شبکه‌های اجتماعی (سطح ۲) ---
def socials_menu_keyboard() -> Dict[str, List[List[Dict[str, Any]]]]:
    """منوی شبکه‌های اجتماعی و لینک‌های خارجی."""
    keyboard = [
        [
            create_button("وبسایت 🖥️", url="https://your-website.com"), 
            create_button("اینستاگرام 📸", url="https://instagram.com/your-page")
        ],
        [create_button("بازگشت به منوی اصلی 🔙", callback_data='MAIN|WELCOME|0')],
    ]
    return create_keyboard(keyboard)

# --- ۷. منوی بازگشت ساده برای حالت‌های ورودی ---
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
