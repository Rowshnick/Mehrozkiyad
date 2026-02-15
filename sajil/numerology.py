# sajil/numerology.py

from typing import Dict


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
EN_DIGITS = "0123456789"


def _to_english_digits(s: str) -> str:
    table = str.maketrans(PERSIAN_DIGITS, EN_DIGITS)
    return s.translate(table)


def life_path_number(birth_date: str) -> int:
    """
    محاسبه عدد مسیر زندگی (Life Path Number) به‌صورت ساده:
    جمع تمام ارقام تاریخ تا رسیدن به یک رقم.
    """
    s = _to_english_digits(birth_date.replace("/", "").replace("-", ""))
    digits = [int(ch) for ch in s if ch.isdigit()]
    total = sum(digits)

    while total > 9:
        total = sum(int(d) for d in str(total))

    return total


def basic_numerology_profile(birth_date: str) -> Dict[str, str]:
    lp = life_path_number(birth_date)
    descriptions = {
        1: "رهبر، آغازگر، مستقل.",
        2: "دیپلمات، همدل، شریک خوب.",
        3: "خلاق، هنرمند، بیان‌گر.",
        4: "منظم، سازنده، پایدار.",
        5: "آزاد، ماجراجو، تغییرپذیر.",
        6: "حامی، خانواده‌محور، مسئول.",
        7: "کاوش‌گر، معنوی، عمیق.",
        8: "قدرت، موفقیت مادی، مدیریت.",
        9: "انسان‌دوست، بخشنده، جهانی.",
    }
    return {
        "life_path_number": str(lp),
        "life_path_description": descriptions.get(lp, "الگوی عددی خاص و منحصربه‌فرد."),
    }
