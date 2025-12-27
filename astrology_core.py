# astrology_core.py
import pytz
from skyfield.api import load, Topos
from persiantools.jdatetime import JalaliDateTime
from typing import Dict, Any

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

try:
    ts = load.timescale()
    eph = load('de421.bsp')
    EPHEMERIS = {k: eph[v] for k, v in PLANET_MAPPING.items()}
    EPHEMERIS['earth'] = eph['earth']
except Exception as e:
    EPHEMERIS = {}
    raise RuntimeError(f"Ephemeris load failed: {e}")

def calculate_natal_chart(
    birth_date_jalali: str,
    birth_time: str,
    city_name: str,
    lat: float,
    lon: float,
    tz_name: str
) -> Dict[str, Any]:

    if not EPHEMERIS:
        return {"error": "Ephemeris not loaded"}

    try:
        jdt = JalaliDateTime.strptime(
            f"{birth_date_jalali} {birth_time}",
            "%Y/%m/%d %H:%M"
        )

        tz = pytz.timezone(tz_name)
        dt_local = tz.localize(jdt.to_gregorian())
        dt_utc = dt_local.astimezone(pytz.utc)
        t = ts.utc(dt_utc)

        observer = EPHEMERIS['earth'] + Topos(
            latitude_degrees=lat,
            longitude_degrees=lon
        )

    except Exception as e:
        return {"error": f"Time conversion error: {e}"}

    result: Dict[str, Any] = {
        "meta": {
            "city": city_name,
            "date": birth_date_jalali,
            "time": birth_time,
            "timezone": tz_name
        },
        "planets": {}
    }

    for p in PLANETS:
        try:
            pos = observer.at(t).observe(EPHEMERIS[p]).apparent()
            lon_rad, _, _ = pos.ecliptic_lonlat()
            result["planets"][p] = {
                "degree": round(lon_rad.degrees, 4)
            }
        except Exception as e:
            result["planets"][p] = {"error": str(e)}

    return result
