# ============================================================
#  CHART ENGINE (LAYER 3)
#  Real chart builder for Roshina Project
#  - سیارات واقعی با Skyfield
#  - خانه‌ها (Placidus / Whole Sign)
#  - نقاط حساس (Node, Lilith, Fortune, Vertex, East Point)
#  - جنبه‌ها (سیارات + نقاط) با ساختار استاندارد p1/p2
# ============================================================

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Literal

# --- Engines ---
from astrology_core.Engine.planets import (
    get_time,
    get_all_planets,
)

from astrology_core.Core.houses import (
    get_asc_mc,
    build_placidus_houses,
    build_whole_sign_houses,
)

from astrology_core.Core.points import (
    get_extra_points,
)

from astrology_core.Core.aspects import (
    compute_all_aspects,
)


ChartDict = Dict[str, Any]
HouseSystem = Literal["placidus", "whole_sign"]


# ------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------

def _build_houses_dict(cusps_list):
    """
    تبدیل لیست ۱۲تایی کاسپ‌ها به دیکشنری استاندارد:
    {
        "Cusp1": {"lon": ...},
        ...
        "Cusp12": {"lon": ...}
    }
    """
    houses = {}
    for i, lon in enumerate(cusps_list, start=1):
        houses[f"Cusp{i}"] = {"lon": float(lon)}
    return houses


def _merge_bodies_for_aspects(planets: Dict[str, Dict[str, Any]],
                              points: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    ادغام سیارات و نقاط برای موتور جنبه‌ها.
    ساختار خروجی:
    {
        "Sun": {"lon": ..., "speed": ...},
        "Moon": {...},
        "Fortune": {"lon": ...},
        ...
    }
    """
    merged = {}

    # سیارات (شامل lon و speed)
    for name, data in planets.items():
        merged[name] = {
            "lon": float(data.get("lon")),
            "speed": float(data.get("speed", 0.0)),
        }

    # نقاط (فقط lon)
    for name, data in points.items():
        merged[name] = {
            "lon": float(data.get("lon")),
        }

    return merged


# ------------------------------------------------------------
#  Main chart builder
# ------------------------------------------------------------

def build_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
    tz_offset: float = 0.0,
    house_system: HouseSystem = "placidus",
) -> ChartDict:
    """
    ساخت یک چارت واقعی (ناتال یا هر لحظهٔ دیگر) بر اساس:
    - تاریخ و زمان
    - مختصات جغرافیایی
    - منطقهٔ زمانی
    - سیستم خانه (Placidus / Whole Sign)

    خروجی:
    {
        "planets": {...},
        "houses": {...},
        "points": {...},
        "aspects": {...},
        "meta": {...}
    }
    """

    # 1) زمان Skyfield
    t = get_time(year, month, day, hour, minute, tz_offset)

    # 2) سیارات (طول دایرةالبروجی + سرعت)
    planets = get_all_planets(t)

    # 3) Asc و MC
    asc_lon, mc_lon = get_asc_mc(t, latitude_deg=lat, longitude_deg=lon)

    # 4) خانه‌ها
    if house_system == "placidus":
        cusps = build_placidus_houses(t, latitude_deg=lat, longitude_deg=lon)
    elif house_system == "whole_sign":
        cusps = build_whole_sign_houses(asc_lon)
    else:
        raise ValueError(f"Unknown house system: {house_system}")

    houses = _build_houses_dict(cusps)

    # 5) نقاط حساس (Node, Lilith, Fortune, Vertex, East Point)
    points = get_extra_points(
        t=t,
        asc=asc_lon,
        mc=mc_lon,
        latitude_deg=lat,
        longitude_deg=lon,
        planets=planets,
    )

    # 6) جنبه‌ها (سیارات + نقاط)
    bodies_for_aspects = _merge_bodies_for_aspects(planets, points)
    raw_aspects = compute_all_aspects(bodies_for_aspects)

    # تبدیل ساختار به فرمت استاندارد p1/p2
    aspects_list = []
    for a in raw_aspects:
        aspects_list.append({
            "p1": a.get("planet1"),
            "p2": a.get("planet2"),
            "type": a.get("type"),
            "orb": a.get("orb"),
            "category": a.get("category"),
        })

    aspects_block = {
        "planet_aspects": aspects_list
    }

    # 7) متادیتا
    dt = datetime(year, month, day, hour, minute)
    meta = {
        "datetime": dt.strftime("%Y-%m-%d %H:%M"),
        "lat": float(lat),
        "lon": float(lon),
        "tz_offset": float(tz_offset),
        "house_system": house_system,
    }

    # 8) ساخت ساختار نهایی چارت
    chart: ChartDict = {
        "planets": planets,
        "houses": houses,
        "points": points,
        "aspects": aspects_block,
        "meta": meta,
    }

    return chart
