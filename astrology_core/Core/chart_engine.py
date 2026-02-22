# astrology_core/Core/chart_engine.py
# نسخهٔ اصلاح‌شده برای معماری جدید

import numpy as np

# =========================
#  IMPORTS (NEW ARCHITECTURE)
# =========================

# زمان و سیارات
from ..Engine.planets import (
    get_time,
    get_all_planets,
)

# سیستم‌های خانه‌ها (فایل جدید تو)
from .houses import (
    get_asc_mc,
    build_equal_houses,
    build_whole_sign_houses,
    build_placidus_houses,
    build_koch_houses,
    build_porphyry_houses,
    build_regiomontanus_houses,
    build_campanus_houses,
)

# جنبه‌ها و میدپوینت‌ها (اگر فایل‌ها موجودند)
try:
    from .aspects import compute_all_aspects
except:
    compute_all_aspects = None

try:
    from .midpoints import build_midpoints
except:
    build_midpoints = None


# =========================
#  انتخاب سیستم خانه‌ها
# =========================

def compute_houses(t, lat, lon, system="placidus"):
    system = system.lower()

    if system == "equal":
        asc, _ = get_asc_mc(t, lat, lon)
        return build_equal_houses(asc)

    elif system == "whole":
        asc, _ = get_asc_mc(t, lat, lon)
        return build_whole_sign_houses(asc)

    elif system == "placidus":
        return build_placidus_houses(t, lat, lon)

    elif system == "koch":
        return build_koch_houses(t, lat, lon)

    elif system == "porphyry":
        return build_porphyry_houses(t, lat, lon)

    elif system == "regiomontanus":
        return build_regiomontanus_houses(t, lat, lon)

    elif system == "campanus":
        return build_campanus_houses(t, lat, lon)

    else:
        raise ValueError(f"Unknown house system: {system}")


# =========================
#  ساخت چارت کامل
# =========================

def build_chart(
    year, month, day,
    hour, minute,
    tz_offset,
    latitude_deg, longitude_deg,
    house_system="placidus",
    include_midpoints=True,
    include_dial90=True,
):
    """
    خروجی: دیکشنری کامل چارت
    """

    # 1) زمان Skyfield
    t = get_time(year, month, day, hour, minute, tz_offset)

    # 2) سیارات
    planets = get_all_planets(t)

    # 3) خانه‌ها
    houses = compute_houses(t, latitude_deg, longitude_deg, house_system)

    # 4) جنبه‌ها
    if compute_all_aspects:
        aspects = compute_all_aspects(planets)
    else:
        aspects = {"planet_aspects": []}

    # 5) میدپوینت‌ها
    if include_midpoints and build_midpoints:
        midpoints = build_midpoints(planets)
    else:
        midpoints = {}

    # 6) خروجی نهایی
    chart = {
        "planets": planets,
        "houses": {f"Cusp{i+1}": {"lon": houses[i]} for i in range(12)},
        "aspects": aspects,
        "midpoints": midpoints,
        "meta": {
            "house_system": house_system,
            "latitude": latitude_deg,
            "longitude": longitude_deg,
            "include_midpoints": include_midpoints,
            "include_dial90": include_dial90,
        }
    }

    return chart
