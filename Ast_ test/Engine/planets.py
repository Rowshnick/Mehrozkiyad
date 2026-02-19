from skyfield.api import load
import numpy as np

# بارگذاری ephemeris دقیق JPL DE440
eph = load('de440.bsp')
ts = load.timescale()

# نگاشت سیارات به آبجکت‌های Skyfield
PLANETS = {
    "Sun": eph["sun"],
    "Moon": eph["moon"],
    "Mercury": eph["mercury"],
    "Venus": eph["venus"],
    "Mars": eph["mars barycenter"],
    "Jupiter": eph["jupiter barycenter"],
    "Saturn": eph["saturn barycenter"],
    "Uranus": eph["uranus barycenter"],
    "Neptune": eph["neptune barycenter"],
    "Pluto": eph["pluto barycenter"],
}

def get_time(year, month, day, hour, minute, second=0, tz_offset=0):
    """
    ساخت زمان Skyfield با امکان تنظیم اختلاف ساعت
    """
    return ts.utc(year, month, day, hour - tz_offset, minute, second)

def ecliptic_lon_lat(body, t):
    """
    محاسبه طول و عرض دایرةالبروجی سیاره نسبت به زمین
    """
    astrometric = eph['earth'].at(t).observe(body).apparent()

    # مختصات استوایی
    ra, dec, distance = astrometric.radec()
    ra_rad = ra.radians
    dec_rad = dec.radians

    # اوبلیکویتی زمین
    eps = np.radians(23.4392911)

    # تبدیل استوایی → دایرةالبروجی
    lon = np.degrees(
        np.arctan2(
            np.sin(ra_rad) * np.cos(eps) + np.tan(dec_rad) * np.sin(eps),
            np.cos(ra_rad),
        )
    ) % 360

    lat = np.degrees(
        np.arcsin(
            np.sin(dec_rad) * np.cos(eps)
            - np.cos(dec_rad) * np.sin(eps) * np.sin(ra_rad)
        )
    )

    return float(lon), float(lat)

def get_all_planets(t):
    """
    خروجی کامل سیارات با طول و عرض دایرةالبروجی
    """
    result = {}
    for name, body in PLANETS.items():
        lon, lat = ecliptic_lon_lat(body, t)
        result[name] = {
            "lon": lon,
            "lat": lat
        }
    return result
