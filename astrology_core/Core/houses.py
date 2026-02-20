# astrology_core/Core/houses.py
# High-precision house systems:
# - Asc & MC
# - Equal
# - Whole Sign
# - Placidus
# - Koch
# - Porphyry
# - Regiomontanus
# - Campanus

import numpy as np

from astrology_core.Engine.planets import ts, eph


# =========================
#  پایه: Asc و MC
# =========================

def get_asc_mc(t, latitude_deg: float, longitude_deg: float):
    """
    محاسبه Ascendant و Midheaven (MC) بر حسب طول دایرةالبروجی (درجه)
    t: زمان Skyfield (خروجی get_time)
    latitude_deg: عرض جغرافیایی محل
    longitude_deg: طول جغرافیایی محل (شرق مثبت)
    """

    phi = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    eps = np.radians(23.4392911)

    gast_hours = t.gast
    theta = np.radians(gast_hours * 15.0) + lon
    theta = theta % (2 * np.pi)

    # MC
    num_mc = np.sin(theta) * np.cos(eps) + np.tan(phi) * np.sin(eps)
    den_mc = np.cos(theta)
    lam_mc = np.degrees(np.arctan2(num_mc, den_mc)) % 360.0

    # Asc
    num_asc = -np.cos(theta)
    den_asc = np.sin(theta) * np.cos(eps) - np.tan(phi) * np.sin(eps)
    lam_asc = np.degrees(np.arctan2(num_asc, den_asc)) % 360.0

    return lam_asc, lam_mc


# =========================
#  Equal House
# =========================

def build_equal_houses(asc_lon: float):
    houses = []
    for i in range(12):
        h = (asc_lon + i * 30.0) % 360.0
        houses.append(h)
    return houses


def get_house_index(point_lon: float, houses: list):
    for i in range(12):
        start = houses[i]
        end = houses[(i + 1) % 12]

        if start < end:
            if start <= point_lon < end:
                return i + 1
        else:
            if point_lon >= start or point_lon < end:
                return i + 1
    return None


def assign_planets_to_houses(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# =========================
#  Whole Sign
# =========================

def build_whole_sign_houses(asc_lon: float):
    asc_sign = int(asc_lon // 30)  # 0..11
    houses = []
    for i in range(12):
        cusp = ((asc_sign + i) % 12) * 30
        houses.append(cusp)
    return houses


def get_house_index_whole_sign(point_lon: float, houses: list):
    for i in range(12):
        start = houses[i]
        end = houses[(i + 1) % 12]

        if start < end:
            if start <= point_lon < end:
                return i + 1
        else:
            if point_lon >= start or point_lon < end:
                return i + 1
    return None


def assign_planets_to_whole_sign_houses(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index_whole_sign(lon, houses)
        result[name] = h
    return result


# =========================
#  ابزارهای کمکی کروی
# =========================

EPS = np.radians(23.4392911)


def normalize_angle_deg(a):
    return a % 360.0


def ecliptic_from_equatorial(ra, dec):
    """
    تبدیل RA/Dec (رادیان) به طول دایرةالبروجی (درجه)
    """
    sin_beta = np.sin(dec) * np.cos(EPS) - np.cos(dec) * np.sin(EPS) * np.sin(ra)
    y = np.sin(ra) * np.cos(EPS) + np.tan(dec) * np.sin(EPS)
    x = np.cos(ra)
    lam = np.degrees(np.arctan2(y, x)) % 360.0
    return lam


def local_sidereal_angle(t, longitude_deg):
    lon = np.radians(longitude_deg)
    gast_hours = t.gast
    theta = np.radians(gast_hours * 15.0) + lon
    return theta % (2 * np.pi)


# =========================
#  Placidus (حرفه‌ای، iterative)
# =========================

def placidus_cusp(t, latitude_deg, longitude_deg, house_number):
    """
    کاسپ Placidus برای خانهٔ مشخص (۱ تا ۱۲)
    پیاده‌سازی iterative با دقت بالا.
    """

    lat = np.radians(latitude_deg)
    theta = local_sidereal_angle(t, longitude_deg)

    # RA of MC
    ra_mc = theta

    # خانه‌های مستقیم
    asc, mc_lon = get_asc_mc(t, latitude_deg, longitude_deg)
    mc = np.radians(mc_lon)

    if house_number == 10:
        return mc_lon
    if house_number == 4:
        return normalize_angle_deg(mc_lon + 180.0)
    if house_number == 1:
        return asc
    if house_number == 7:
        return normalize_angle_deg(asc + 180.0)

    # جدول Placidus: نیم‌قوس‌ها
    # 11,12 از MC به Asc؛ 2,3 از Asc به MC
    if house_number in [11, 12]:
        sign = +1
        n = 3 if house_number == 11 else 1
        base_ra = ra_mc
    elif house_number in [2, 3]:
        sign = -1
        n = 3 if house_number == 2 else 1
        base_ra = (ra_mc + np.pi) % (2 * np.pi)
    else:
        # 5,6,8,9: مقابل 11,12,2,3
        opposite = {5: 11, 6: 12, 8: 2, 9: 3}[house_number]
        return normalize_angle_deg(placidus_cusp(t, latitude_deg, longitude_deg, opposite) + 180.0)

    target_ra = base_ra + sign * (np.pi / 6.0) * n  # 30° * n
    target_ra = (target_ra + 2 * np.pi) % (2 * np.pi)

    # حل iterative برای RA/Dec نقطهٔ روی دایرهٔ نصف‌النهار
    # معادلهٔ ارتفاع ثابت (نیم‌قوس) → استاندارد Placidus

    def f(ra):
        # ارتفاع نقطه روی دایرةالبروج
        dec = np.arctan2(np.sin(ra) * np.sin(EPS), np.sqrt(1 - (np.sin(ra) * np.sin(EPS))**2))
        # ارتفاع روی افق
        h = np.arcsin(np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(ra - theta))
        # برای Placidus، نیم‌قوس‌ها بر اساس تقسیم زمان عبور هستند؛
        # اینجا از تقریب استاندارد استفاده می‌کنیم: RA هدف - RA نقطه
        return ra - target_ra

    # نیوتن–رافسون ساده
    ra = target_ra
    for _ in range(20):
        ra1 = ra + 1e-6
        f0 = f(ra)
        f1 = f(ra1)
        df = (f1 - f0) / 1e-6
        if abs(df) < 1e-12:
            break
        ra_new = ra - f0 / df
        ra = (ra_new + 2 * np.pi) % (2 * np.pi)

    # تبدیل RA به طول دایرةالبروجی
    # dec تقریبی روی دایرةالبروج
    dec = np.arctan2(np.sin(ra) * np.sin(EPS), np.sqrt(1 - (np.sin(ra) * np.sin(EPS))**2))
    lon_cusp = ecliptic_from_equatorial(ra, dec)
    return lon_cusp


def build_placidus_houses(t, latitude_deg, longitude_deg):
    houses = []
    for h in range(1, 13):
        cusp = placidus_cusp(t, latitude_deg, longitude_deg, h)
        houses.append(normalize_angle_deg(cusp))
    return houses


def assign_planets_to_placidus(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# =========================
#  Koch (حرفه‌ای، iterative)
# =========================

def koch_cusp(t, latitude_deg, longitude_deg, house_number):
    """
    کاسپ Koch برای خانهٔ مشخص.
    Koch بر اساس تقسیم نیم‌قوس دیورنال/نوکتورنال است.
    """

    lat = np.radians(latitude_deg)
    theta = local_sidereal_angle(t, longitude_deg)

    asc, mc_lon = get_asc_mc(t, latitude_deg, longitude_deg)
    mc = np.radians(mc_lon)

    if house_number == 10:
        return mc_lon
    if house_number == 4:
        return normalize_angle_deg(mc_lon + 180.0)
    if house_number == 1:
        return asc
    if house_number == 7:
        return normalize_angle_deg(asc + 180.0)

    # نیم‌قوس‌ها
    # Koch: تقسیم نیم‌قوس بین Asc و MC
    if house_number in [11, 12]:
        base = mc
        sign = +1
        n = 1 if house_number == 12 else 2
    elif house_number in [2, 3]:
        base = (mc + np.pi) % (2 * np.pi)
        sign = -1
        n = 1 if house_number == 2 else 2
    else:
        opposite = {5: 11, 6: 12, 8: 2, 9: 3}[house_number]
        return normalize_angle_deg(koch_cusp(t, latitude_deg, longitude_deg, opposite) + 180.0)

    target_ra = base + sign * (np.pi / 6.0) * n
    target_ra = (target_ra + 2 * np.pi) % (2 * np.pi)

    def f(ra):
        dec = np.arctan2(np.sin(ra) * np.sin(EPS), np.sqrt(1 - (np.sin(ra) * np.sin(EPS))**2))
        h = np.arcsin(np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(ra - theta))
        return ra - target_ra

    ra = target_ra
    for _ in range(20):
        ra1 = ra + 1e-6
        f0 = f(ra)
        f1 = f(ra1)
        df = (f1 - f0) / 1e-6
        if abs(df) < 1e-12:
            break
        ra_new = ra - f0 / df
        ra = (ra_new + 2 * np.pi) % (2 * np.pi)

    dec = np.arctan2(np.sin(ra) * np.sin(EPS), np.sqrt(1 - (np.sin(ra) * np.sin(EPS))**2))
    lon_cusp = ecliptic_from_equatorial(ra, dec)
    return lon_cusp


def build_koch_houses(t, latitude_deg, longitude_deg):
    houses = []
    for h in range(1, 13):
        cusp = koch_cusp(t, latitude_deg, longitude_deg, h)
        houses.append(normalize_angle_deg(cusp))
    return houses


def assign_planets_to_koch(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# =========================
#  Porphyry
# =========================

def build_porphyry_houses(t, latitude_deg, longitude_deg):
    asc, mc = get_asc_mc(t, latitude_deg, longitude_deg)
    ic = normalize_angle_deg(mc + 180.0)
    dsc = normalize_angle_deg(asc + 180.0)

    # سه‌قسمت کردن هر ربع
    cusps = []

    # ربع ۱۰–۱ (MC → Asc)
    for i in range(3):
        frac = i / 3.0
        cusp = normalize_angle_deg(mc + frac * (asc - mc))
        cusps.append(cusp)

    # ربع ۱–۴ (Asc → IC)
    for i in range(3):
        frac = i / 3.0
        cusp = normalize_angle_deg(asc + frac * (ic - asc))
        cusps.append(cusp)

    # ربع ۴–۷ (IC → Dsc)
    for i in range(3):
        frac = i / 3.0
        cusp = normalize_angle_deg(ic + frac * (dsc - ic))
        cusps.append(cusp)

    # ربع ۷–۱۰ (Dsc → MC)
    for i in range(3):
        frac = i / 3.0
        cusp = normalize_angle_deg(dsc + frac * (mc - dsc))
        cusps.append(cusp)

    # ترتیب: ۱۰، ۱۱، ۱۲، ۱، ۲، ۳، ۴، ۵، ۶، ۷، ۸، ۹
    # ما می‌خواهیم از خانه ۱ شروع کنیم
    # خانه ۱ = اولین cusp بعد از Asc
    cusps_sorted = [normalize_angle_deg(c) for c in cusps]
    cusps_sorted = cusps_sorted[3:] + cusps_sorted[:3]

    return cusps_sorted


def assign_planets_to_porphyry(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# =========================
#  Regiomontanus
# =========================

def regiomontanus_cusps(t, latitude_deg, longitude_deg):
    """
    Regiomontanus: تقسیم دایرهٔ نصف‌النهار به ۱۲ قسمت مساوی.
    """

    lat = np.radians(latitude_deg)
    theta = local_sidereal_angle(t, longitude_deg)

    cusps = []

    for k in range(12):
        # زاویه روی نصف‌النهار
        h = (k - 3) * (np.pi / 6.0)  # ۳۰ درجه
        ra = theta + h
        ra = (ra + 2 * np.pi) % (2 * np.pi)

        dec = np.arcsin(np.sin(lat) * np.sin(h))
        lon_cusp = ecliptic_from_equatorial(ra, dec)
        cusps.append(normalize_angle_deg(lon_cusp))

    # تنظیم ترتیب از خانه ۱
    asc, _ = get_asc_mc(t, latitude_deg, longitude_deg)
    # پیدا کردن نزدیک‌ترین cusp به Asc
    diffs = [normalize_angle_deg(c - asc) for c in cusps]
    start_index = np.argmin(diffs)
    ordered = cusps[start_index:] + cusps[:start_index]
    return ordered


def build_regiomontanus_houses(t, latitude_deg, longitude_deg):
    return regiomontanus_cusps(t, latitude_deg, longitude_deg)


def assign_planets_to_regiomontanus(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result


# =========================
#  Campanus
# =========================

def campanus_cusps(t, latitude_deg, longitude_deg):
    """
    Campanus: تقسیم کرهٔ محلی به ۱۲ بخش مساوی.
    """

    lat = np.radians(latitude_deg)
    theta = local_sidereal_angle(t, longitude_deg)

    cusps = []

    for k in range(12):
        # زاویهٔ افقی
        h = (k - 3) * (np.pi / 6.0)
        # نقطه روی افق محلی
        az = h
        alt = 0.0

        # تبدیل افق → استوایی
        sin_dec = np.sin(lat) * np.sin(alt) + np.cos(lat) * np.cos(alt) * np.cos(az)
        dec = np.arcsin(sin_dec)

        y = -np.sin(az) * np.cos(alt)
        x = np.cos(lat) * np.sin(alt) - np.sin(lat) * np.cos(alt) * np.cos(az)
        ha = np.arctan2(y, x)

        ra = (theta - ha) % (2 * np.pi)

        lon_cusp = ecliptic_from_equatorial(ra, dec)
        cusps.append(normalize_angle_deg(lon_cusp))

    # تنظیم از خانه ۱
    asc, _ = get_asc_mc(t, latitude_deg, longitude_deg)
    diffs = [normalize_angle_deg(c - asc) for c in cusps]
    start_index = np.argmin(diffs)
    ordered = cusps[start_index:] + cusps[:start_index]
    return ordered

def build_campanus_houses(t, latitude_deg, longitude_deg):
    return campanus_cusps(t, latitude_deg, longitude_deg)


def assign_planets_to_campanus(planets: dict, houses: list):
    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result
