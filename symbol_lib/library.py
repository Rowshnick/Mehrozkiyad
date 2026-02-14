"""
library.py
مرکز تجمیع تمام نمادها از دسته‌های مختلف فرهنگی، معنوی و جهانی.
"""

# -----------------------------
#   ایمپورت صحیح مطابق ساختار
# -----------------------------

from .symbols.iranian import IRANIAN_SYMBOLS
from .symbols.greek_roman import GREEK_ROMAN_SYMBOLS
from .symbols.hindu import HINDU_SYMBOLS
from .symbols.chinese import CHINESE_SYMBOLS
from .symbols.ottoman import OTTOMAN_SYMBOLS
from .symbols.kabbalah import KABBALAH_SYMBOLS
from .symbols.egyptian import EGYPTIAN_SYMBOLS
from .symbols.mesopotamia import MESOPOTAMIA_SYMBOLS
from .symbols.celtics import CELTIC_SYMBOLS
from .symbols.buddhist import BUDDHIST_SYMBOLS
from .symbols.shamanic import SHAMANIC_SYMBOLS
from .symbols.sacred_geometry import SACRED_GEOMETRY_SYMBOLS
from .symbols.global_archetypes import GLOBAL_ARCHETYPES


# -----------------------------
#   دیکشنری مرکزی
# -----------------------------

SYMBOLS: dict = {}

SYMBOLS.update(IRANIAN_SYMBOLS)
SYMBOLS.update(GREEK_ROMAN_SYMBOLS)
SYMBOLS.update(HINDU_SYMBOLS)
SYMBOLS.update(CHINESE_SYMBOLS)
SYMBOLS.update(OTTOMAN_SYMBOLS)
SYMBOLS.update(KABBALAH_SYMBOLS)
SYMBOLS.update(EGYPTIAN_SYMBOLS)
SYMBOLS.update(MESOPOTAMIA_SYMBOLS)
SYMBOLS.update(CELTIC_SYMBOLS)
SYMBOLS.update(BUDDHIST_SYMBOLS)
SYMBOLS.update(SHAMANIC_SYMBOLS)
SYMBOLS.update(SACRED_GEOMETRY_SYMBOLS)
SYMBOLS.update(GLOBAL_ARCHETYPES)


# -----------------------------
#   توابع کمکی
# -----------------------------

def get_symbol(symbol_id: str) -> dict | None:
    return SYMBOLS.get(symbol_id)


def list_symbols() -> list[str]:
    return list(SYMBOLS.keys())
