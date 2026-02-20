# astrology_core/Core/chart_engine.py

from astrology_core.Engine.planets import get_time, get_all_planets
from astrology_core.Core.houses import (
    get_asc_mc,
    build_equal_houses,
    build_whole_sign_houses,
    build_placidus_houses,
    assign_planets_to_houses,
    assign_planets_to_whole_sign_houses,
    assign_planets_to_placidus,
)
from astrology_core.Core.points import get_extra_points


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def get_sign_index(lon: float) -> int:
    """برگرداندن شمارهٔ نشانه (۰ تا ۱۱) بر اساس طول دایرةالبروجی"""
    return int(lon // 30) % 12


def get_sign_name(lon: float) -> str:
    return ZODIAC_SIGNS[get_sign_index(lon)]


def annotate_planets_with_signs(planets: dict):
    """
    به هر سیاره، نام نشانه و درجهٔ داخل نشانه را اضافه می‌کند.
    """
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        sign_idx = get_sign_index(lon)
        sign_name = ZODIAC_SIGNS[sign_idx]
        deg_in_sign = lon % 30

        enriched = dict(data)
        enriched["sign"] = sign_name
        enriched["sign_index"] = sign_idx
        enriched["deg_in_sign"] = deg_in_sign

        result[name] = enriched

    return result


def build_chart(
    year, month, day,
    hour, minute, tz_offset,
    latitude_deg, longitude_deg,
    house_system: str = "placidus"
):
    """
    ساخت چارت کامل:
    - سیارات
    - نشانه‌ها
    - خانه‌ها (Equal / Whole / Placidus)
    - نقاط اضافی (MC, Vertex, POF)
    """

    # زمان
    t = get_time(year, month, day, hour, minute, tz_offset)

    # سیارات
    planets = get_all_planets(t)
    planets = annotate_planets_with_signs(planets)

    # Asc و MC
    asc, mc = get_asc_mc(t, latitude_deg, longitude_deg)

    # خانه‌ها
    house_system = house_system.lower()
    if house_system == "equal":
        houses = build_equal_houses(asc)
        planet_houses = assign_planets_to_houses(planets, houses)
    elif house_system == "whole":
        houses = build_whole_sign_houses(asc)
        planet_houses = assign_planets_to_whole_sign_houses(planets, houses)
    elif house_system == "placidus":
        houses = build_placidus_houses(t, latitude_deg, longitude_deg)
        planet_houses = assign_planets_to_placidus(planets, houses)
    else:
        raise ValueError(f"Unknown house system: {house_system}")

    # نقاط اضافی (MC ساده، Vertex، POF)
    sun_lon = planets["Sun"]["lon"]
    moon_lon = planets["Moon"]["lon"]
    extra_points = get_extra_points(t, latitude_deg, longitude_deg, asc, sun_lon, moon_lon)

    # اضافه کردن خانه‌ها به سیارات
    for name in planets.keys():
        planets[name]["house"] = planet_houses.get(name)

    chart = {
        "time": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "tz_offset": tz_offset,
        },
        "location": {
            "lat": latitude_deg,
            "lon": longitude_deg,
        },
        "house_system": house_system,
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "planets": planets,
        "extra_points": extra_points,
    }

    return chart
