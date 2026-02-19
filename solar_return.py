##%%writefile Mehrozkiyad/astrology_engine/engine/solar_return.py
import numpy as np
from .planets import get_all_planets, get_time, ts
from .houses import placidus_houses, get_ascendant, get_mc
from .points import get_extra_points
from .aspects import detect_aspects

# طول خورشید در یک زمان
def sun_longitude(t):
    return get_all_planets(t)["Sun"]["lon"]

# پیدا کردن لحظه دقیق بازگشت خورشید
def find_solar_return_time(natal_sun_lon, year, month, day, hour, minute, tz_offset):
    # بازه جستجو: ۲ روز
    t1 = get_time(year, month, day, hour, minute, tz_offset)
    t2 = get_time(year, month, day + 2, hour, minute, tz_offset)

    for _ in range(40):  # دقت بالا
        tm = ts.tt_jd((t1.tt + t2.tt) / 2)
        lon_m = sun_longitude(tm)

        diff = (lon_m - natal_sun_lon + 540) % 360 - 180

        if diff > 0:
            t2 = tm
        else:
            t1 = tm

    return t1

# چارت کامل Solar Return
def compute_solar_return(
    natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz,
    birth_lat, birth_lon,
    sr_year, sr_month, sr_day, sr_hour, sr_minute, sr_tz,
    current_lat, current_lon
):
    # خورشید ناتال
    t_natal = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)
    natal_sun_lon = sun_longitude(t_natal)

    # لحظه دقیق Solar Return
    t_sr = find_solar_return_time(natal_sun_lon, sr_year, sr_month, sr_day, sr_hour, sr_minute, sr_tz)

    # سیارات
    planets = get_all_planets(t_sr)

    # نقاط اصلی در مکان فعلی
    asc = get_ascendant(t_sr, current_lat, current_lon)
    mc = get_mc(t_sr, current_lon)
    houses = placidus_houses(t_sr, current_lat, current_lon)

    # نقاط اضافی
    sun_lon = planets["Sun"]["lon"]
    moon_lon = planets["Moon"]["lon"]
    extra = get_extra_points(t_sr, current_lat, current_lon, asc, sun_lon, moon_lon)

    # جنبه‌ها
    all_points = {**planets, **extra}
    aspects = detect_aspects(all_points)

    return {
        "solar_return_time": t_sr.tt,
        "planets": planets,
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "extra_points": extra,
        "aspects": aspects,
    }
