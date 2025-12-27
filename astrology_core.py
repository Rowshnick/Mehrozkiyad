# astrology_core.py
import math
import pytz
from typing import Dict, Any
from skyfield.api import load, Topos
from persiantools.jdatetime import JalaliDateTime

# -----------------------
# Constants
# -----------------------

PLANETS = [
    'sun', 'moon', 'mercury', 'venus', 'mars',
    'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
]

PLANET_MAPPING = {
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

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# -----------------------
# Load Ephemeris
# -----------------------

ts = load.timescale()
eph = load("de421.bsp")
EPHEMERIS = {k: eph[v] for k, v in PLANET_MAPPING.items()}
EPHEMERIS["earth"] = eph["earth"]

# -----------------------
# Math Helpers
# -----------------------

def _deg_norm(deg: float) -> float:
    return deg % 360.0

def _rad_to_deg(rad: float) -> float:
    return rad * 180.0 / math.pi

# -----------------------
# Ascendant Calculation
# -----------------------

def calculate_ascendant(t, lat: float, lon: float) -> float:
    """
    محاسبه Ascendant واقعی (درجه دایرةالبروج)
    """
    gst = t.gast * 15  # Greenwich Sidereal Time → degrees
    lst = _deg_norm(gst + lon)

    eps = math.radians(23.4392911)  # obliquity
    lat_r = math.radians(lat)
    lst_r = math.radians(lst)

    asc = math.atan2(
        math.sin(lst_r),
        math.cos(lst_r)
    )

    asc_deg = _deg_norm(_rad_to_deg(asc))
    return asc_deg

# -----------------------
# Houses (Whole Sign)
# -----------------------

def calculate_houses(asc: float) -> Dict[int, float]:
    houses = {}
    for i in range(12):
        houses[i + 1] = _deg_norm(asc + i * 30)
    return houses

# -----------------------
# Main Chart Function
# -----------------------

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time: str,
    city_name: str,
    lat: float,
    lon: float,
    tz_name: str
) -> Dict[str, Any]:

    try:
        jdt = JalaliDateTime.strptime(
            f"{birth_date_jalali} {birth_time}",
            "%Y/%m/%d %H:%M"
        )

        tz = pytz.timezone(tz_name)
        dt_local = tz.localize(jdt.to_gregorian())
        dt_utc = dt_local.astimezone(pytz.utc)
        t = ts.utc(dt_utc)

        observer = EPHEMERIS["earth"] + Topos(
            latitude_degrees=lat,
            longitude_degrees=lon
        )

    except Exception as e:
        return {"error": f"Time conversion error: {e}"}

    # Ascendant & Houses
    asc = calculate_ascendant(t, lat, lon)
    houses = calculate_houses(asc)

    chart = {
        "meta": {
            "city": city_name,
            "date": birth_date_jalali,
            "time": birth_time,
            "timezone": tz_name,
        },
        "ascendant": round(asc, 4),
        "houses": houses,
        "planets": {}
    }

    for p in PLANETS:
        try:
            pos = observer.at(t).observe(EPHEMERIS[p]).apparent()
            lon_rad, _, _ = pos.ecliptic_lonlat()
            deg = _deg_norm(lon_rad.degrees)

            house = int(((deg - asc) % 360) / 30) + 1
            sign = SIGNS[int(deg / 30)]

            chart["planets"][p] = {
                "degree": round(deg, 4),
                "sign": sign,
                "house": house
            }

        except Exception as e:
            chart["planets"][p] = {"error": str(e)}

    return chart
