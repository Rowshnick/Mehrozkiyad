# transits.py
# موتور ترانزیت هماهنگ با موتور جدید جنبه‌ها و ساختار p1/p2

from __future__ import annotations
from typing import Dict, Any

from astrology_core.Engine.planets import get_all_planets, get_time
from astrology_core.Core.aspects import compute_all_aspects


def compute_transits_to_natal(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int,
    natal_minute: int,
    natal_tz: float,
    natal_lat: float,
    natal_lon: float,
    transit_year: int,
    transit_month: int,
    transit_day: int,
    transit_hour: int,
    transit_minute: int,
    transit_tz: float,
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

    # زمان ترانزیت
    transit_t = get_time(
        transit_year,
        transit_month,
        transit_day,
        transit_hour,
        transit_minute,
        transit_tz,
    )
    transit_planets = get_all_planets(transit_t)

    # ادغام برای موتور جنبه‌ها
    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in transit_planets.items():
        combined[f"T_{name}"] = data

    # محاسبهٔ جنبه‌ها
    raw_aspects = compute_all_aspects(combined)

    # فقط جنبه‌های N ↔ T و تبدیل به ساختار p1/p2
    aspects_list = []
    for a in raw_aspects:
        p1 = a["planet1"]
        p2 = a["planet2"]
        if (p1.startswith("N_") and p2.startswith("T_")) or \
           (p1.startswith("T_") and p2.startswith("N_")):
            aspects_list.append({
                "p1": p1,
                "p2": p2,
                "type": a.get("type"),
                "orb": a.get("orb"),
                "category": None,
            })

    return {
        "natal": natal_planets,
        "transit": transit_planets,
        "aspects": aspects_list,
    }
