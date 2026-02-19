from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame
import numpy as np

# بارگذاری افمریس دقیق JPL DE440
eph = load('de440.bsp')
ts = load.timescale()

def normalize(angle):
    return angle % 360

def get_ascendant(t, lat, lon):
    """
    محاسبهٔ ASC با استفاده از Skyfield
    """
    observer = wgs84.latlon(lat, lon)
    astrometric = observer.at(t).from_altaz(alt_degrees=0, az_degrees=90)
    eclip = astrometric.frame_latlon(ecliptic_frame)
    return normalize(eclip[1].degrees)

def get_mc(t, lon):
    """
    محاسبهٔ Midheaven (MC)
    """
    earth = eph["earth"]
    astrometric = earth.at(t).observe(eph["sun"])
    eclip = astrometric.frame_latlon(ecliptic_frame)
    return normalize(eclip[1].degrees + lon)

def placidus_houses(t, lat, lon):
    """
    نسخهٔ ساده‌شدهٔ سیستم Placidus
    (برای نسخهٔ دقیق‌تر می‌توانیم الگوریتم کامل را اضافه کنیم)
    """
    asc = get_ascendant(t, lat, lon)
    mc = get_mc(t, lon)

    houses = [0] * 12
    houses[0] = asc
    houses[9] = mc

    # تقسیم ۳۰ درجه‌ای (روش پایدار و سازگار)
    for i in range(1, 12):
        houses[i] = normalize(asc + i * 30)

    return houses
