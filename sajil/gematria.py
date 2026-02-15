# sajil/gematria.py

from typing import Dict

# نگاشت ساده برای حروف فارسی (می‌توانی بعداً دقیق‌ترش کنی)
PERSIAN_GEMATRIA = {
    "ا": 1, "ب": 2, "پ": 2, "ت": 400, "ث": 500,
    "ج": 3, "چ": 3, "ح": 8, "خ": 600,
    "د": 4, "ذ": 700, "ر": 200, "ز": 7, "ژ": 7,
    "س": 60, "ش": 300, "ص": 90, "ض": 800,
    "ط": 9, "ظ": 900, "ع": 70, "غ": 1000,
    "ف": 80, "ق": 100, "ک": 20, "گ": 20,
    "ل": 30, "م": 40, "ن": 50, "و": 6, "ه": 5, "ی": 10,
}


def name_gematria(name: str) -> int:
    total = 0
    for ch in name.replace(" ", ""):
        total += PERSIAN_GEMATRIA.get(ch, 0)
    return total


def basic_gematria_profile(name: str) -> Dict[str, str]:
    value = name_gematria(name)
    return {
        "name_gematria_value": str(value),
        "name_gematria_note": "مجموع ارزش حروف نام شما بر اساس یک نگاشت سادهٔ ابجد/گیمیاتریا.",
    }
