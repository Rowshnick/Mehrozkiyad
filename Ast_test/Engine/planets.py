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
    t = ts.utc(year, month, day, hour - tz_offset, minute, second)
    return t

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

# ---------------------------------------------------------
# ⭐ تابع جدید: Declination
# ---------------------------------------------------------

def get_declination(body, t):
    """
    محاسبه Declination (میل) سیاره نسبت به زمین
    """
    astrometric = eph['earth'].at(t).observe(body).apparent()
    ra, dec, distance = astrometric.radec()
    return float(dec.degrees)

# ---------------------------------------------------------
# ⭐ تابع جدید: سرعت و Retrograde
# ---------------------------------------------------------

def compute_speed_and_retrograde(body, t):
    """
    محاسبه سرعت طولی، سرعت عرضی و وضعیت Retrograde
    """

    dt = 0.5  # نیم‌روز برای دقت بهتر

    t_prev = t - dt
    t_next = t + dt

    # موقعیت قبل
    lon_prev, lat_prev = ecliptic_lon_lat(body, t_prev)

    # موقعیت بعد
    lon_next, lat_next = ecliptic_lon_lat(body, t_next)

    # سرعت طولی
    speed_lon = (lon_next - lon_prev) / (2 * dt)

    # اصلاح عبور از 360
    if speed_lon > 180:
        speed_lon -= 360
    if speed_lon < -180:
        speed_lon += 360

    # سرعت عرضی
    speed_lat = (lat_next - lat_prev) / (2 * dt)

    # retrograde؟
    retrograde = speed_lon < 0

    return speed_lon, speed_lat, retrograde

# ---------------------------------------------------------
# ⭐ تابع اصلی: خروجی کامل سیارات
# ---------------------------------------------------------

def get_all_planets(t):
    """
    خروجی کامل سیارات با:
    - طول دایرةالبروجی
    - عرض دایرةالبروجی
    - Declination
    - سرعت طولی
    - سرعت عرضی
    - Retrograde
    """
    result = {}
    for name, body in PLANETS.items():
        lon, lat = ecliptic_lon_lat(body, t)

        # محاسبه Declination
        dec = get_declination(body, t)

        # محاسبه سرعت و R/D
        speed_lon, speed_lat, retrograde = compute_speed_and_retrograde(body, t)

        result[name] = {
            "lon": lon,
            "lat": lat,
            "declination": dec,
            "speed_lon": speed_lon,
            "speed_lat": speed_lat,
            "retrograde": retrograde
        }

    return result

def get_declination_aspects(planets, orb=1.0):
    """
    محاسبه Parallel و Contra-Parallel بین سیارات
    ورودی:
        planets = خروجی get_all_planets
        orb = حداکثر اختلاف میل (درجه)
    خروجی:
        لیست جنبه‌ها
    """

    names = list(planets.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1 = names[i]
            p2 = names[j]

            dec1 = planets[p1]["declination"]
            dec2 = planets[p2]["declination"]

            # Parallel
            if (dec1 * dec2 > 0) and (abs(dec1 - dec2) <= orb):
                aspects.append({
                    "type": "Parallel",
                    "p1": p1,
                    "p2": p2,
                    "orb": abs(dec1 - dec2)
                })

            # Contra-Parallel
            if (dec1 * dec2 < 0) and (abs(dec1 + dec2) <= orb):
                aspects.append({
                    "type": "Contra-Parallel",
                    "p1": p1,
                    "p2": p2,
                    "orb": abs(dec1 + dec2)
                })

    return aspects

def get_oob_planets(planets):
    """
    تشخیص سیارات Out-Of-Bounds بر اساس Declination
    ورودی:
        planets = خروجی get_all_planets
    خروجی:
        لیست سیارات OOB
    """

    OBB_LIMIT = 23.44  # حد میل خورشید

    oob_list = []

    for name, data in planets.items():
        dec = abs(data["declination"])
        if dec > OBB_LIMIT:
            oob_list.append({
                "planet": name,
                "declination": data["declination"],
                "amount": dec - OBB_LIMIT
            })

    return oob_list

def get_latitude_aspects(planets, orb=1.0):
    """
    محاسبه Parallel و Contra-Parallel بر اساس عرض دایرةالبروجی (Latitude)

    ورودی:
        planets = خروجی get_all_planets
        orb = حداکثر اختلاف عرض (درجه)

    خروجی:
        لیست جنبه‌ها
    """

    names = list(planets.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1 = names[i]
            p2 = names[j]

            lat1 = planets[p1]["lat"]
            lat2 = planets[p2]["lat"]

            # Parallel (Latitude)
            if (lat1 * lat2 > 0) and (abs(lat1 - lat2) <= orb):
                aspects.append({
                    "type": "Lat-Parallel",
                    "p1": p1,
                    "p2": p2,
                    "orb": abs(lat1 - lat2)
                })

            # Contra-Parallel (Latitude)
            if (lat1 * lat2 < 0) and (abs(lat1 + lat2) <= orb):
                aspects.append({
                    "type": "Lat-Contra-Parallel",
                    "p1": p1,
                    "p2": p2,
                    "orb": abs(lat1 + lat2)
                })

    return aspects
    
    
