# astrology_core/Core/chart_engine.py
# لایهٔ دوم: موتور ساخت چارت حرفه‌ای
# - محاسبه زمان
# - محاسبه سیارات
# - محاسبه نقاط اضافی
# - انتخاب سیستم خانه‌ها
# - نسبت دادن سیارات به خانه‌ها
# - خروجی استاندارد و دقیق

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


# ============================
#  موتور اصلی ساخت چارت
# ============================

def build_chart(
    year, month, day,
    hour, minute,
    tz_offset,
    latitude_deg, longitude_deg,
    house_system="placidus"
):
    """
    ساخت چارت کامل:
    - محاسبه زمان Skyfield
    - محاسبه سیارات
    - محاسبه Asc و MC
    - محاسبه خانه‌ها (بر اساس سیستم انتخابی)
    - نسبت دادن سیارات به خانه‌ها
    - محاسبه نقاط اضافی
    """

    # -------------------------
    # 1) زمان Skyfield
    # -------------------------
    t = get_time(year, month, day, hour, minute, tz_offset)

    # -------------------------
    # 2) سیارات
    # -------------------------
    planets = get_all_planets(t)

    # -------------------------
    # 3) Asc و MC
    # -------------------------
    asc, mc = get_asc_mc(t, latitude_deg, longitude_deg)

    # -------------------------
    # 4) سیستم خانه‌ها
    # -------------------------
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

    # -------------------------
    # 5) نقاط اضافی (Node, Lilith, Part of Fortune...)
    # -------------------------
    extra_points = get_extra_points(t, asc, mc, latitude_deg, longitude_deg)

    # -------------------------
    # 6) خروجی نهایی
    # -------------------------
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
        }
    }

    return chart
