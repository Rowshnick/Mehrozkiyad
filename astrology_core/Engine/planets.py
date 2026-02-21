# astrology_core/Engine/planets.py
# موتور سیارات با Skyfield — شامل سرعت دقیق

from skyfield.api import load
import numpy as np

# بارگذاری افمریس
eph = load('de421.bsp')
ts = load.timescale()

PLANET_MAP = {
    "Sun": eph['sun'],
    "Moon": eph['moon'],
    "Mercury": eph['mercury'],
    "Venus": eph['venus'],
    "Mars": eph['mars'],
    "Jupiter": eph['jupiter barycenter'],
    "Saturn": eph['saturn barycenter'],
    "Uranus": eph['uranus barycenter'],
    "Neptune": eph['neptune barycenter'],
    "Pluto": eph['pluto barycenter'],
}

def get_time(year, month, day, hour, minute, tz_offset):
    # تبدیل به UTC
    hour_utc = hour - tz_offset
    return ts.utc(year, month, day, hour_utc, minute)

def ecliptic_lon(body, t):
    """طول دایرةالبروجی دقیق"""
    e = body.at(t).ecliptic_position().au
    x, y, z = e
    lon = np.degrees(np.arctan2(y, x)) % 360.0
    return lon

def ecliptic_speed(body, t):
    """
    سرعت طولی سیاره (درجه در روز)
    با محاسبهٔ مشتق عددی بسیار دقیق
    """
    dt = 1e-4  # ~8.6 ثانیه
    t2 = ts.tt_jd(t.tt + dt)
    lon1 = ecliptic_lon(body, t)
    lon2 = ecliptic_lon(body, t2)
    d = (lon2 - lon1) % 360.0
    if d > 180:
        d -= 360
    speed = d / dt  # deg/day
    return speed

def get_all_planets(t):
    """
    خروجی:
    {
        "Sun": {
            "lon": ...,
            "speed": ...,
            "sign": ...,
            "deg_in_sign": ...
        },
        ...
    }
    """

    result = {}

    for name, body in PLANET_MAP.items():
        lon = ecliptic_lon(body, t)
        speed = ecliptic_speed(body, t)

        sign_index = int(lon // 30)
        deg_in_sign = lon % 30

        result[name] = {
            "lon": lon,
            "speed": speed,
            "sign": sign_index,
            "deg_in_sign": deg_in_sign,
        }

    return result
