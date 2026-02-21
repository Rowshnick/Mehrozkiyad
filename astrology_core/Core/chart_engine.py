# astrology_core/Core/chart_engine.py
# لایهٔ دوم: موتور ساخت چارت حرفه‌ای
# - محاسبه زمان
# - محاسبه سیارات
# - محاسبه نقاط اضافی
# - انتخاب سیستم خانه‌ها
# - نسبت دادن سیارات به خانه‌ها
# - خروجی استاندارد و دقیق
# astrology_core/Core/chart_engine.py

import numpy as np

from astrology_core.Engine.planets import (
    get_time,
    get_all_planets,
)

from astrology_core.Core.houses import (
    get_asc_mc,
    build_equal_houses,
    build_whole_sign_houses,
    build_placidus_houses,
    build_koch_houses,
    build_porphyry_houses,
    build_regiomontanus_houses,
    build_campanus_houses,

    assign_planets_to_houses,
    assign_planets_to_whole_sign_houses,
    assign_planets_to_placidus,
    assign_planets_to_koch,
    assign_planets_to_porphyry,
    assign_planets_to_regiomontanus,
    assign_planets_to_campanus,
)

from astrology_core.Core.points import get_extra_points
from astrology_core.Core.aspects import compute_all_aspects
from astrology_core.Core.midpoints import (
    build_midpoints,
    compute_midpoint_aspects,
    compute_midpoint_to_midpoint_aspects,
)
from astrology_core.Core.dial90 import (
    build_90_points,
    find_90_midpoints,
)


def build_chart(
    year, month, day,
    hour, minute,
    tz_offset,
    latitude_deg, longitude_deg,
    house_system="placidus",
    include_midpoints=True,
    include_dial90=True,
):
    # 1) زمان
    t = get_time(year, month, day, hour, minute, tz_offset)

    # 2) سیارات
    planets = get_all_planets(t)  # dict[name] = {"lon": ..., "speed": optional}

    # 3) Asc و MC
    asc, mc = get_asc_mc(t, latitude_deg, longitude_deg)

    # 4) خانه‌ها
    house_system = house_system.lower().strip()

    if house_system == "equal":
        houses = build_equal_houses(asc)
        planet_houses = assign_planets_to_houses(planets, houses)

    elif house_system == "whole":
        houses = build_whole_sign_houses(asc)
        planet_houses = assign_planets_to_whole_sign_houses(planets, houses)

    elif house_system == "placidus":
        houses = build_placidus_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_placidus(planets, houses)

    elif house_system == "koch":
        houses = build_koch_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_koch(planets, houses)

    elif house_system == "porphyry":
        houses = build_porphyry_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_porphyry(planets, houses)

    elif house_system == "regiomontanus":
        houses = build_regiomontanus_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_regiomontanus(planets, houses)

    elif house_system == "campanus":
        houses = build_campanus_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_campanus(planets, houses)

    else:
        raise ValueError(f"سیستم خانه‌ها ناشناخته است: {house_system}")

    # 5) نقاط اضافی
    extra_points = get_extra_points(t, asc, mc, latitude_deg, longitude_deg, planets)
    # فرض: extra_points[name]["lon"]

    # 6) ساخت مجموعهٔ کامل نقاط برای Aspect Engine
    bodies = {}

    # سیارات
    for name, data in planets.items():
        bodies[name] = {
            "lon": data.get("lon"),
            "speed": data.get("speed"),
        }

    # زاویه‌ها
    bodies["Asc"] = {"lon": asc}
    bodies["MC"] = {"lon": mc}
    bodies["IC"] = {"lon": (mc + 180.0) % 360.0}
    bodies["Dsc"] = {"lon": (asc + 180.0) % 360.0}

    # کاسپ خانه‌ها
    for i, cusp in enumerate(houses, start=1):
        bodies[f"Cusp{i}"] = {"lon": cusp}

    # نقاط اضافی
    for name, data in extra_points.items():
        lon = data.get("lon")
        if lon is None:
            continue
        bodies[name] = {"lon": lon}

    # 7) جنبه‌های بین همهٔ نقاط
    planet_aspects = compute_all_aspects(bodies)

    # 8) Midpoints
    midpoints = {}
    midpoint_aspects = []
    midpoint_midpoint_aspects = []

    if include_midpoints:
        midpoints = build_midpoints(bodies, pairs=None)  # همهٔ ترکیب‌ها (سنگین ولی کامل)
        # midpoint → planet/point/cusp
        midpoint_aspects = compute_midpoint_aspects(midpoints, bodies)
        # midpoint → midpoint
        midpoint_midpoint_aspects = compute_midpoint_to_midpoint_aspects(midpoints)

    # 9) 90° Dial
    dial90 = None
    if include_dial90:
        pts90 = build_90_points(bodies)
        mids90 = find_90_midpoints(pts90, max_orb=1.0)
        dial90 = {
            "points": pts90,
            "midpoints": mids90,
        }

    chart = {
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "planets": planets,
        "planet_houses": planet_houses,
        "extra_points": extra_points,
        "house_system": house_system,
        "location": {
            "latitude": latitude_deg,
            "longitude": longitude_deg,
        },
        "datetime": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "tz_offset": tz_offset,
        },
        "aspects": {
            "planet_aspects": planet_aspects,
            "midpoints": midpoints,
            "midpoint_aspects": midpoint_aspects,
            "midpoint_midpoint_aspects": midpoint_midpoint_aspects,
            "dial90": dial90,
        },
    }

    return chart
