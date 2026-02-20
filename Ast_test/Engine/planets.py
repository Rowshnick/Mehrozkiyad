from skyfield.api import load
import numpy as np

# ---------------------------------------------------------
# بارگذاری Ephemeris دقیق JPL DE440
# ---------------------------------------------------------
eph = load('de440.bsp')
ts = load.timescale()

# ---------------------------------------------------------
# نگاشت سیارات به آبجکت‌های Skyfield
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# ساخت زمان Skyfield با درنظر گرفتن اختلاف ساعت
# ---------------------------------------------------------
def get_time(year, month, day, hour, minute, second=0, tz_offset=0):
    return ts.utc(year, month, day, hour - tz_offset, minute, second)

# ---------------------------------------------------------
# محاسبه طول و عرض دایرةالبروجی (Ecliptic Lon/Lat)
# ---------------------------------------------------------
def ecliptic_lon_lat(body, t):
    astrometric = eph['earth'].at(t).observe(body).apparent()

    ra, dec, distance = astrometric.radec()
    ra_rad = ra.radians
    dec_rad = dec.radians

    eps = np.radians(23.4392911)  # اوبلیکویتی زمین

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
# محاسبه Declination (میل)
# ---------------------------------------------------------
def get_declination(body, t):
    astrometric = eph['earth'].at(t).observe(body).apparent()
    ra, dec, distance = astrometric.radec()
    return float(dec.degrees)

# ---------------------------------------------------------
# محاسبه سرعت طولی/عرضی و Retrograde
# ---------------------------------------------------------
def compute_speed_and_retrograde(body, t):
    dt = 0.5  # نیم‌روز

    t_prev = t - dt
    t_next = t + dt

    lon_prev, lat_prev = ecliptic_lon_lat(body, t_prev)
    lon_next, lat_next = ecliptic_lon_lat(body, t_next)

    speed_lon = (lon_next - lon_prev) / (2 * dt)

    # اصلاح عبور از 360
    if speed_lon > 180:
        speed_lon -= 360
    if speed_lon < -180:
        speed_lon += 360

    speed_lat = (lat_next - lat_prev) / (2 * dt)

    retrograde = speed_lon < 0

    return speed_lon, speed_lat, retrograde

# ---------------------------------------------------------
# خروجی کامل سیارات
# ---------------------------------------------------------
def get_all_planets(t):
    result = {}
    for name, body in PLANETS.items():
        lon, lat = ecliptic_lon_lat(body, t)
        dec = get_declination(body, t)
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

# ---------------------------------------------------------
# جنبه‌های Declination (Parallel / Contra-Parallel)
# ---------------------------------------------------------
def get_declination_aspects(planets, orb=1.0):
    names = list(planets.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            dec1 = planets[p1]["declination"]
            dec2 = planets[p2]["declination"]

            if (dec1 * dec2 > 0) and (abs(dec1 - dec2) <= orb):
                aspects.append({
                    "type": "Parallel",
                    "p1": p1, "p2": p2,
                    "orb": abs(dec1 - dec2)
                })

            if (dec1 * dec2 < 0) and (abs(dec1 + dec2) <= orb):
                aspects.append({
                    "type": "Contra-Parallel",
                    "p1": p1, "p2": p2,
                    "orb": abs(dec1 + dec2)
                })

    return aspects

# ---------------------------------------------------------
# تشخیص سیارات Out-Of-Bounds
# ---------------------------------------------------------
def get_oob_planets(planets):
    OBB_LIMIT = 23.44
    oob_list = []

    for name, data in planets.items():
        dec_abs = abs(data["declination"])
        if dec_abs > OBB_LIMIT:
            oob_list.append({
                "planet": name,
                "declination": data["declination"],
                "amount": dec_abs - OBB_LIMIT
            })

    return oob_list

# ---------------------------------------------------------
# جنبه‌های Latitude (Lat-Parallel / Lat-Contra-Parallel)
# ---------------------------------------------------------
def get_latitude_aspects(planets, orb=1.0):
    names = list(planets.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            lat1 = planets[p1]["lat"]
            lat2 = planets[p2]["lat"]

            if (lat1 * lat2 > 0) and (abs(lat1 - lat2) <= orb):
                aspects.append({
                    "type": "Lat-Parallel",
                    "p1": p1, "p2": p2,
                    "orb": abs(lat1 - lat2)
                })

            if (lat1 * lat2 < 0) and (abs(lat1 + lat2) <= orb):
                aspects.append({
                    "type": "Lat-Contra-Parallel",
                    "p1": p1, "p2": p2,
                    "orb": abs(lat1 + lat2)
                })

    return aspects

# ---------------------------------------------------------
# جنبه‌های طولی (Longitude Aspects)
# ---------------------------------------------------------
def get_longitude_aspects(planets, orb_major=6.0, orb_minor=3.0):
    ASPECTS = {
        "Conjunction": 0,
        "Semi-Sextile": 30,
        "Semi-Square": 45,
        "Sextile": 60,
        "Square": 90,
        "Trine": 120,
        "Quincunx": 150,
        "Sesquiquadrate": 135,
        "Opposition": 180,
    }

    names = list(planets.keys())
    results = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            lon1 = planets[p1]["lon"]
            lon2 = planets[p2]["lon"]

            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff

            for asp_name, asp_angle in ASPECTS.items():
                orb = orb_major if asp_name in ["Conjunction", "Opposition", "Square", "Trine"] else orb_minor

                if abs(diff - asp_angle) <= orb:
                    results.append({
                        "type": asp_name,
                        "p1": p1, "p2": p2,
                        "orb": abs(diff - asp_angle),
                        "angle": diff
                    })

    return results

# ---------------------------------------------------------
# استانداردسازی ساختار جنبه‌ها
# ---------------------------------------------------------
def normalize_aspect(aspect):
    base = {
        "type": aspect.get("type"),
        "category": aspect.get("category"),
        "p1": aspect.get("p1"),
        "p2": aspect.get("p2"),
        "orb": aspect.get("orb"),
        "angle": None,
        "lat_diff": None,
        "dec_diff": None,
    }

    if aspect["category"] == "Longitude":
        base["angle"] = aspect.get("angle")

    if aspect["category"] == "Declination":
        base["dec_diff"] = aspect.get("orb")

    if aspect["category"] == "Latitude":
        base["lat_diff"] = aspect.get("orb")

    return base

# ---------------------------------------------------------
# موتور کامل جنبه‌ها (Aspect Engine)
# ---------------------------------------------------------
def get_aspect_engine(
    planets,
    orb_lon_major=6.0,
    orb_lon_minor=3.0,
    orb_dec=1.0,
    orb_lat=1.0,
    include_lon=True,
    include_dec=True,
    include_lat=True
):
    aspects = []

    if include_lon:
        for a in get_longitude_aspects(planets, orb_lon_major, orb_lon_minor):
            a["category"] = "Longitude"
            aspects.append(normalize_aspect(a))

    if include_dec:
        for a in get_declination_aspects(planets, orb_dec):
            a["category"] = "Declination"
            aspects.append(normalize_aspect(a))

    if include_lat:
        for a in get_latitude_aspects(planets, orb_lat):
            a["category"] = "Latitude"
            aspects.append(normalize_aspect(a))

    return aspects
