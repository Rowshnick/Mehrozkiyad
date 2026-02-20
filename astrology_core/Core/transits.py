# astrology_core/Core/transits.py

from astrology_core.Engine.planets import get_all_planets, get_time
from astrology_core.Core.aspect_tools import get_aspect_engine

def compute_transits_to_natal(
    natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz,
    natal_lat, natal_lon,
    transit_year, transit_month, transit_day, transit_hour, transit_minute, transit_tz
):
    # زمان ناتال
    t_natal = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)

    # زمان ترانزیت
    t_transit = get_time(transit_year, transit_month, transit_day, transit_hour, transit_minute, transit_tz)

    # سیارات ناتال و ترانزیت
    natal_planets = get_all_planets(t_natal)
    transit_planets = get_all_planets(t_transit)

    # ادغام برای موتور جنبه‌ها
    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in transit_planets.items():
        combined[f"T_{name}"] = data

    # جنبه‌ها
    aspects = get_aspect_engine(combined)

    # فقط جنبه‌های بین ناتال و ترانزیت
    inter_aspects = [
        a for a in aspects
        if (a["p1"].startswith("N_") and a["p2"].startswith("T_"))
        or (a["p1"].startswith("T_") and a["p2"].startswith("N_"))
    ]

    return {
        "natal_planets": natal_planets,
        "transit_planets": transit_planets,
        "inter_aspects": inter_aspects,
    }
