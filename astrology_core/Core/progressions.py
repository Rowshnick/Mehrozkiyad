# progressions.py
# موتور پروگرشن ثانویه هماهنگ با موتور جدید جنبه‌ها

from __future__ import annotations
from typing import Dict, Any

from astrology_core.Engine.planets import get_all_planets, get_time
from astrology_core.Core.aspects import compute_all_aspects


def progressed_time(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int,
    natal_minute: int,
    natal_tz: float,
    age_years: float,
):
    """
    Secondary Progression:
    هر 1 روز بعد از تولد = 1 سال زندگی
    """
    progressed_day = natal_day + age_years
    return get_time(
        natal_year,
        natal_month,
        progressed_day,
        natal_hour,
        natal_minute,
        natal_tz,
    )


def compute_secondary_progressions(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int,
    natal_minute: int,
    natal_tz: float,
    natal_lat: float,
    natal_lon: float,
    age_years: float,
) -> Dict[str, Any]:

    # زمان ناتال
    natal_t = get_time(
        natal_year,
        natal_month,
        natal_day,
        natal_hour,
        natal_minute,
        natal_tz,
    )
    natal_planets = get_all_planets(natal_t)

    # زمان پروگرشن
    prog_t = progressed_time(
        natal_year,
        natal_month,
        natal_day,
        natal_hour,
        natal_minute,
        natal_tz,
        age_years,
    )
    progressed_planets = get_all_planets(prog_t)

    # ادغام برای موتور جنبه‌ها
    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in progressed_planets.items():
        combined[f"P_{name}"] = data

    # محاسبهٔ جنبه‌ها
    aspects = compute_all_aspects(combined)

    # فقط جنبه‌های N ↔ P
    result = []
    for a in aspects:
        p1 = a["p1"]
        p2 = a["p2"]
        if (p1.startswith("N_") and p2.startswith("P_")) or (p1.startswith("P_") and p2.startswith("N_")):
            result.append(a)

    return {
        "natal": natal_planets,
        "progressed": progressed_planets,
        "aspects": result,
    }
