# ============================================================
#  CHART ENGINE (REAL VERSION)
#  Fully rewritten by Roshina Project
#  Placidus = default house system
#  Whole Sign = optional
# ============================================================

from datetime import datetime
from typing import Dict, Any

# --- Skyfield-based planet engine ---
from .planets import get_time, get_all_planets

# --- House systems ---
from astrology_core.Core.houses import (
    build_placidus_houses,
    build_whole_sign_houses,
)

# --- Aspect engine ---
from astrology_core.Core.aspects import compute_all_aspects

# --- Sensitive points ---
from astrology_core.Core.points import get_extra_points


# ============================================================
#  MAIN ENGINE
# ============================================================

def build_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
    tz_offset: float = 0.0,
    house_system: str = "placidus",
) -> Dict[str, Any]:
    """
    ساخت چارت واقعی با Skyfield + موتور جنبه + سیستم خانه‌ها + نقاط حساس.

    خروجی:
    {
        "planets": {...},
        "houses": {...},
        "aspects": {...},
        "points": {...},
        "meta": {...}
    }
    """

    # --------------------------------------------------------
    # 1) زمان Skyfield
    # --------------------------------------------------------
    t = get_time(year, month, day, hour, minute, tz_offset)

    # --------------------------------------------------------
    # 2) سیارات (lon + speed + sign + deg_in_sign)
    # --------------------------------------------------------
    planets = get_all_planets(t)

    # --------------------------------------------------------
    # 3) سیستم خانه‌ها
    # --------------------------------------------------------
    if house_system.lower() == "placidus":
        cusps = build_placidus_houses(t, lat, lon)
    elif house_system.lower() == "whole_sign":
        # Whole Sign از Asc شروع می‌شود
        asc = planets["Asc"]["lon"] if "Asc" in planets else None
        if asc is None:
            # اگر Asc در planets نبود، باید از houses.py محاسبه شود
            from astrology_core.Core.houses import get_asc_mc
            asc, _ = get_asc_mc(t, lat, lon)
        cusps = build_whole_sign_houses(asc)
    else:
        raise ValueError(f"Unknown house system: {house_system}")

    houses = {f"Cusp{i+1}": {"lon": cusps[i]} for i in range(12)}

    # --------------------------------------------------------
    # 4) نقاط حساس (Node, Lilith, Fortune, Vertex, East Point)
    # --------------------------------------------------------
    # Asc و MC لازم هستند
    from astrology_core.Core.houses import get_asc_mc
    asc, mc = get_asc_mc(t, lat, lon)

    points = get_extra_points(
        t=t,
        asc=asc,
        mc=mc,
        latitude_deg=lat,
        longitude_deg=lon,
        planets=planets,
    )

    # --------------------------------------------------------
    # 5) جنبه‌ها (major + minor + applying + strength)
    # --------------------------------------------------------
    # bodies = planets + points + cusps (اختیاری)
    bodies = {}

    # سیارات
    for k, v in planets.items():
        bodies[k] = {"lon": v["lon"], "speed": v["speed"]}

    # نقاط حساس
    for k, v in points.items():
        bodies[k] = {"lon": v["lon"]}

    # کاسپ‌ها (اختیاری – اگر بخواهی می‌توانیم حذف کنیم)
    for i in range(12):
        bodies[f"Cusp{i+1}"] = {"lon": cusps[i]}

    aspects = compute_all_aspects(bodies)

    # --------------------------------------------------------
    # 6) ساخت خروجی نهایی
    # --------------------------------------------------------
    chart = {
        "planets": planets,
        "houses": houses,
        "aspects": {"planet_aspects": aspects},
        "points": points,
        "meta": {
            "datetime": f"{year}-{month}-{day} {hour}:{minute}",
            "lat": lat,
            "lon": lon,
            "tz_offset": tz_offset,
            "house_system": house_system,
        },
    }

    return chart
