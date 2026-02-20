# astrology_core/Core/progressions.py

from astrology_core.Engine.planets import get_all_planets, get_time, ts
from astrology_core.Core.aspect_tools import get_aspect_engine

def progressed_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz, age_years):
    t0 = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)
    jd_progressed = t0.tt + age_years
    return ts.tt_jd(jd_progressed)

def compute_secondary_progressions(
    natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz,
    natal_lat, natal_lon,
    age_years
):
    t_natal = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)
    t_prog = progressed_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz, age_years)

    natal_planets = get_all_planets(t_natal)
    prog_planets = get_all_planets(t_prog)

    # ادغام سیارات ناتال و پروگرس‌شده
    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in prog_planets.items():
        combined[f"P_{name}"] = data

    # جنبه‌ها
    aspects = get_aspect_engine(combined)

    # فقط جنبه‌های بین ناتال و پروگرس‌شده
    inter_aspects = [
        a for a in aspects
        if (a["p1"].startswith("N_") and a["p2"].startswith("P_"))
        or (a["p1"].startswith("P_") and a["p2"].startswith("N_"))
    ]

    return {
        "natal_planets": natal_planets,
        "progressed_planets": prog_planets,
        "inter_aspects": inter_aspects,
        "progressed_time": t_prog.tt,
    }
