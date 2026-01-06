"""
library.py
مرکز تجمیع تمام نمادها از دسته‌های مختلف فرهنگی، معنوی و جهانی.

این فایل فقط نقش "کتابخانهٔ مرکزی" را دارد و هیچ منطق تجاری (business logic)
داخل آن قرار نمی‌گیرد. هر دستهٔ نماد در یک فایل جداگانه در پوشهٔ symbols
تعریف شده است و اینجا فقط ایمپورت و ادغام می‌شود.

برای اضافه‌کردن یک دستهٔ جدید:
1. تعریف دیکشنری در فایل مربوطه (مثلاً symbols/new_culture.py)
2. import دیکشنری اینجا
3. SYMBOLS.update(NEW_CULTURE_SYMBOLS)
"""

from .symbols.iranian import IRANIAN_SYMBOLS
from .symbols.greek_roman import GREEK_ROMAN_SYMBOLS
from .symbols.hindu import HINDU_SYMBOLS
from .symbols.chinese import CHINESE_SYMBOLS
from .symbols.ottoman import OTTOMAN_SYMBOLS
from .symbols.kabbalah import KABBALAH_SYMBOLS
from .symbols.egyptian import EGYPTIAN_SYMBOLS
from .symbols.mesopotamian import MESOPOTAMIAN_SYMBOLS
from .symbols.celtic import CELTIC_SYMBOLS
from .symbols.buddhist import BUDDHIST_TIBETAN_SYMBOLS
from .symbols.shamanic import SHAMANIC_SYMBOLS
from .symbols.sacred_geometry import SACRED_GEOMETRY_SYMBOLS
from .symbols.global_archetypes import GLOBAL_ARCHETYPES

# اگر در آینده دسته‌های جدید اضافه شوند، فقط کافی است:
# from .symbols.new_category import NEW_CATEGORY_SYMBOLS
# و بعد:
# SYMBOLS.update(NEW_CATEGORY_SYMBOLS)


# دیکشنری مرکزی تمام نمادها
SYMBOLS: dict = {}

# ادغام تمام دسته‌ها در یک دیکشنری واحد
SYMBOLS.update(IRANIAN_SYMBOLS)
SYMBOLS.update(GREEK_ROMAN_SYMBOLS)
SYMBOLS.update(HINDU_SYMBOLS)
SYMBOLS.update(CHINESE_SYMBOLS)
SYMBOLS.update(OTTOMAN_SYMBOLS)
SYMBOLS.update(KABBALAH_SYMBOLS)
SYMBOLS.update(EGYPTIAN_SYMBOLS)
SYMBOLS.update(MESOPOTAMIAN_SYMBOLS)
SYMBOLS.update(CELTIC_SYMBOLS)
SYMBOLS.update(BUDDHIST_TIBETAN_SYMBOLS)
SYMBOLS.update(SHAMANIC_SYMBOLS)
SYMBOLS.update(SACRED_GEOMETRY_SYMBOLS)
SYMBOLS.update(GLOBAL_ARCHETYPES)


def get_symbol(symbol_id: str) -> dict | None:
    """
    برگرداندن نماد بر اساس کلید (id).
    اگر پیدا نشود، None برمی‌گرداند.
    """
    return SYMBOLS.get(symbol_id)


def list_symbols() -> list[str]:
    """
    لیست تمام کلیدهای نمادها را برمی‌گرداند.
    برای دیباگ، آمار گرفتن یا ساخت منوها کاربردی است.
    """
    return list(SYMBOLS.keys())
