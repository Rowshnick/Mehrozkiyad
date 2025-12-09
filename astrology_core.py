# ----------------------------------------------------------------------
# astrology_core.py - ماژول اصلی محاسبات آسترولوژی (نسخه نهایی و پایدار)
# ----------------------------------------------------------------------

import os
import math
import datetime
from typing import Dict, Any, Optional

from skyfield.api import load, wgs84, Loader
from persiantools.jdatetime import JalaliDateTime
import pytz

# ----------------------------------------------------------------------
# تنظیمات و ثابت‌ها
# ----------------------------------------------------------------------

PLANETS = [
    'sun', 'moon', 'mercury', 'venus', 'mars',
    'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
]

PLANET_TARGETS = {
    'sun': 'sun',
    'moon': 'moon',
    'mercury': 'mercury',
    'venus': 'venus',
    'mars': 'mars',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter',
}

ZODIAC_SIGNS_EN = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

DEFAULT_EPHEMERIS_FILE = os.getenv("EPHEMERIS_FILE", "de421.bsp")
EPHEMERIS_DIR = os.getenv("EPHEMERIS_DIR", "data/ephemeris")
os.makedirs(EPHEMERIS_DIR, exist_ok=True)

loader = Loader(EPHEMERIS_DIR)
ts = load.timescale()

# ----------------------------------------------------------------------
# بارگذاری اپهمریس
# ----------------------------------------------------------------------

def load_ephemeris() -> Optional[dict]:
    try:
        eph_path = os.path.join(EPHEMERIS_DIR, DEFAULT_EPHEMERIS_FILE)
        eph = loader(DEFAULT_EPHEMERIS_FILE) if os.path.exists(eph_path) else load(DEFAULT_EPHEMERIS_FILE)
    except Exception:
        try:
            eph = loader("de440s.bsp")
        except Exception:
            try:
                eph = load("de421.bsp")
            except Exception:
                return None

    ephem_map = {'earth': eph['earth']}
    for key, target in PLANET_TARGETS.items():
        try:
            ephem_map[key] = eph[target]
        except Exception:
            ephem_map[key] = None
    return ephem_map

EPHEMERIS = load_ephemeris()

# ----------------------------------------------------------------------
# ابزارهای زمان و مکان
# ----------------------------------------------------------------------

def to_utc_from_jalali(jalali_date_str: str, time_str: str, timezone_str: str):
    try:
        j_dt = JalaliDateTime.strptime(f"{jalali_date_str} {time_str}", "%Y/%m/%d %H:%M")
        g_dt_naive = j_dt.to_gregorian()
        tz = pytz.timezone(timezone_str)
        g_dt_local = tz.localize(g_dt_naive, is_dst=None)
        g_dt_utc = g_dt_local.astimezone(pytz.utc)
        return g_dt_utc
    except Exception as e:
        raise ValueError(f"خطا در تبدیل زمان/تایم‌زون: {e}")

def sign_name_from_longitude(lon_deg: float) -> str:
    idx = int(math.floor(lon_deg % 360.0) // 30)
    return ZODIAC_SIGNS_EN[idx]

# ----------------------------------------------------------------------
# محاسبه موقعیت سیارات
# ----------------------------------------------------------------------

def compute_planet_positions(dt_utc, latitude: float, longitude: float) -> Dict[str, Any]:
    if EPHEMERIS is None:
        return {"error": "Ephemeris بارگذاری نشد."}

    try:
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
        location = wgs84.latlon(latitude, longitude)
        observer = EPHEMERIS['earth'] + location
    except Exception as e:
        return {"error": f"خطا در آماده‌سازی زمان/مکان: {e}"}

    results: Dict[str, Any] = {}
    for planet in PLANETS:
        try:
            target = EPHEMERIS.get(planet)
            if target is None:
                results[planet] = {"error": "هدف ephemeris یافت نشد."}
                continue

            position = observer.at(t).observe(target).apparent()
            lon, lat, distance = position.ecliptic_latlon()
            lon_deg = float(lon.degrees)

            results[planet] = {
                "longitude_deg": lon_deg,
                "sign": sign_name_from_longitude(lon_deg),
            }
        except Exception as e:
            results[planet] = {"error": f"خطا در محاسبه سیاره: {e}"}

    return results

# ----------------------------------------------------------------------
# تابع اصلی: محاسبه چارت تولد
# ----------------------------------------------------------------------

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time_str: str,
    city_name: str,
    latitude: float,
    longitude: float,
    timezone_str: str
) -> Dict[str, Any]:
    if EPHEMERIS is None:
        return {"error": "داده‌های Ephemeris در دسترس نیست."}

    try:
        dt_utc = to_utc_from_jalali(birth_date_jalali, birth_time_str, timezone_str)
    except Exception as e:
        return {"error": str(e)}

    planets = compute_planet_positions(dt_utc, latitude, longitude)
    if "error" in planets:
        return planets

    return {
        "input": {
            "birth_date_jalali": birth_date_jalali,
            "birth_time": birth_time_str,
            "city": city_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str,
        },
        "datetime_utc": dt_utc.isoformat(),
        "planets": planets,
        "ascendant": None,
        "status": "ok"
    }

# ----------------------------------------------------------------------
# تابع جدید: پیشگویی روزانه
# ----------------------------------------------------------------------

def calculate_daily_prediction(
    birth_date_jalali: str,
    birth_time_str: str,
    city_name: str,
    latitude: float,
    longitude: float,
    timezone_str: str,
    target_date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    if EPHEMERIS is None:
        return {"error": "Ephemeris بارگذاری نشد."}

    if target_date is None:
        target_date = datetime.date.today()

    try:
        dt_birth_utc = to_utc_from_jalali(birth_date_jalali, birth_time_str, timezone_str)
    except Exception as e:
        return {"error": f"خطا در تبدیل زمان تولد: {e}"}

    natal_chart = calculate_natal_chart(
        birth_date_jalali, birth_time_str, city_name, latitude, longitude, timezone_str
    )
    if "error" in natal_chart:
        return natal_chart

    t_today = ts.utc(target_date.year, target_date.month, target_date.day)
    location = wgs84.latlon(latitude, longitude)
    observer = EPHEMERIS['earth'] + location

    today_positions = {}
    for planet in PLANETS:
        try:
            target = EPHEMERIS.get(planet)
            if target is None:
                continue
            pos = observer.at(t_today).observe(target).apparent()
            lon, lat, dist = pos.ecliptic_latlon()
            today_positions[planet] = lon.degrees
        except Exception:
            today_positions[planet] = None

    predictions = []
    natal_planets = natal_chart.get("planets", {})
    for planet, natal_data in natal_planets.items():
        natal_lon = natal_data.get("longitude_deg")
        today_lon = today_positions.get(planet)
        if natal_lon and today_lon:
            diff = abs(today_lon - natal_lon) % 360
            if diff < 8:
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما هم‌نشین است → انرژی مشابه و پررنگ.")
            elif abs(diff - 120) < 8:
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما در تریگون است → هماهنگی و فرصت‌های مثبت.")
            elif abs(diff - 90) < 8:
                predictions.append(f"{planet.capitalize()} امروز با موقعیت تولد شما در مربع است → چالش و فشار احتمالی.")
            elif abs(diff - 180) < 8:
                predictions.append(f"{planet.capitalize()}
