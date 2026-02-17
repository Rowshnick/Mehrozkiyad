from skyfield.api import load, Angle
import numpy as np

# بارگذاری ephemeris دقیق JPL DE440
eph = load('de440.bsp')
ts = load.timescale()

PLANETS = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

def get_time(year, month, day, hour, minute, tz_offset=0):
    """تبدیل زمان محلی به UTC و ساخت آبجکت Skyfield Time"""
    return ts.utc(year, month, day, hour - tz_offset, minute)

def ecliptic_lon_lat(body_name: str, t):
    """محاسبه طول و عرض دایره‌البروجی سیاره"""
    body = eph[PLANETS[body_name]]
    earth = eph['earth']
    astrometric = earth.at(t).observe(body)
    ecliptic = astrometric.ecliptic_position()

    lon = Angle(radians=ecliptic.longitude.radians).degrees % 360
    lat = Angle(radians=ecliptic.latitude.radians).degrees

    return lon, lat

def get_all_planets(t):
    """محاسبه موقعیت تمام سیارات"""
    result = {}
    for name in PLANETS:
        lon, lat = ecliptic_lon_lat(name, t)
        result[name] = {
            "lon": lon,
            "lat": lat
        }
    return result
