from skyfield.api import load, wgs84
import numpy as np

eph = load('de440.bsp')
ts = load.timescale()

def normalize(angle):
    return angle % 360

# ------------------ ASC & MC ------------------

def get_ascendant(t, lat, lon):
    observer = wgs84.latlon(lat, lon)
    astrometric = observer.at(t).from_altaz(alt_degrees=0, az_degrees=90)
    ra, dec, _ = astrometric.radec()

    eps = np.radians(23.4392911)
    ra_rad = ra.radians
    dec_rad = dec.radians

    lon = np.degrees(
        np.arctan2(
            np.sin(ra_rad) * np.cos(eps) + np.tan(dec_rad) * np.sin(eps),
            np.cos(ra_rad)
        )
    ) % 360

    return lon

def get_mc(t, lon):
    gst = t.gast
    lst = (gst + lon / 15) % 24
    ra_mc = lst * 15
    eps = np.radians(23.4392911)
    ra_rad = np.radians(ra_mc)
    lon_mc = np.degrees(np.arctan2(np.sin(ra_rad) * np.cos(eps), np.cos(ra_rad))) % 360
    return lon_mc

# ------------------ سیستم‌های ساده ------------------

def houses_equal(asc):
    return [normalize(asc + i * 30) for i in range(12)]

def houses_whole_sign(asc):
    sign_start = int(asc // 30) * 30
    return [normalize(sign_start + i * 30) for i in range(12)]

def houses_porphyry(asc, mc):
    dsc = normalize(asc + 180)
    ic = normalize(mc + 180)

    def divide_arc(start, end):
        arc = (end - start) % 360
        return [normalize(start + arc * i / 3) for i in range(3)]

    c1 = asc
    c10 = mc
    c7 = dsc
    c4 = ic

    seg_1_10 = divide_arc(c1, c10)
    seg_10_7 = divide_arc(c10, c7)
    seg_7_4 = divide_arc(c7, c4)
    seg_4_1 = divide_arc(c4, c1)

    cusps = [0]*12
    cusps[0] = c1
    cusps[9] = c10
    cusps[6] = c7
    cusps[3] = c4

    cusps[11], cusps[10] = seg_1_10[1], seg_1_10[2]
    cusps[8], cusps[7] = seg_10_7[1], seg_10_7[2]
    cusps[5], cusps[4] = seg_7_4[1], seg_7_4[2]
    cusps[2], cusps[1] = seg_4_1[1], seg_4_1[2]

    return cusps

# ------------------ سیستم‌های حرفه‌ای (در حال توسعه) ------------------

def _deg2rad(d):
    return np.radians(d)

def _rad2deg(r):
    return np.degrees(r)

def _tan(d):
    return np.tan(_deg2rad(d))

def _atan(d):
    return _rad2deg(np.arctan(d))

def _sin(d):
    return np.sin(_deg2rad(d))

def _asin(x):
    return _rad2deg(np.arcsin(x))

def _cos(d):
    return np.cos(_deg2rad(d))

def _acos(x):
    return _rad2deg(np.arccos(x))

def _normalize_360(d):
    return d % 360

def _lst_degrees(t, lon):
    gst = t.gast  # ساعت نجومی گرینویچ (ساعت)
    lst = (gst + lon / 15.0) % 24.0
    return lst * 15.0  # درجه

def _placidus_cusp(lat, obliquity, lst_deg, n):
    """
    n = 1,2,3 برای نیم‌خانه‌های بالا (۱۰، ۱۱، ۱۲)
    n = -1,-2,-3 برای نیم‌خانه‌های پایین (۴، ۵، ۶)
    """
    phi = lat
    eps = obliquity

    # زاویه ساعتی MC
    h_mc = lst_deg - 0  # RA MC ~ LST در این تقریب

    # زاویه ساعتی برای این cusp
    h = h_mc + n * 30.0

    # فرمول Placidus (تقریبی و استاندارد)
    # tan(δ) = cos(φ) * tan(ε) * sin(H)
    # tan(A) = tan(H) * cos(ε) / cos(δ)
    sinH = _sin(h)
    cosH = _cos(h)

    tan_eps = _tan(eps)
    cos_phi = _cos(phi)

    # declination
    tan_delta = cos_phi * tan_eps * sinH
    delta = _atan(tan_delta)

    cos_delta = _cos(delta)
    if abs(cos_delta) < 1e-6:
        cos_delta = 1e-6

    tanA = (cosH * _cos(eps)) / cos_delta
    A = _atan(tanA)

    # تبدیل به طول دایرةالبروجی
    if sinH < 0:
        A = _normalize_360(A + 180)

    return _normalize_360(A)

def houses_placidus(t, lat, lon, asc, mc):
    """
    پیاده‌سازی Placidus (تقریب استاندارد و قابل اتکا)
    """
    # میل محور دایرةالبروج
    eps = 23.4392911  # می‌توانی بعداً از Skyfield هم بگیری

    lst_deg = _lst_degrees(t, lon)

    # خانه‌های ۱۰ و ۴ و ۱ و ۷
    c10 = mc
    c4 = _normalize_360(mc + 180)
    c1 = asc
    c7 = _normalize_360(asc + 180)

    # نیم‌خانه‌های بالا (۱۰–۱۱–۱۲–۱)
    c11 = _placidus_cusp(lat, eps, lst_deg, +1)
    c12 = _placidus_cusp(lat, eps, lst_deg, +2)

    # نیم‌خانه‌های پایین (۴–۵–۶–۷)
    c5 = _placidus_cusp(lat, eps, lst_deg, -1)
    c6 = _placidus_cusp(lat, eps, lst_deg, -2)

    # بقیه خانه‌ها با تقارن
    c2 = _normalize_360(c8 := _normalize_360(c5 + 180))
    c3 = _normalize_360(c9 := _normalize_360(c6 + 180))

    cusps = [0]*12
    cusps[0] = c1
    cusps[1] = c2
    cusps[2] = c3
    cusps[3] = c4
    cusps[4] = c5
    cusps[5] = c6
    cusps[6] = c7
    cusps[7] = c8
    cusps[8] = c9
    cusps[9] = c10
    cusps[10] = c11
    cusps[11] = c12

    return [normalize(c) for c in cusps]












def houses_koch(t, lat, lon, asc, mc):
    raise NotImplementedError("Koch در مرحلهٔ بعدی پیاده‌سازی می‌شود.")

def houses_regiomontanus(t, lat, lon, asc, mc):
    raise NotImplementedError("Regiomontanus در مرحلهٔ بعدی پیاده‌سازی می‌شود.")

# ------------------ رابط اصلی ------------------

def compute_houses(t, lat, lon, system="placidus", asc=None, mc=None):
    if asc is None:
        asc = get_ascendant(t, lat, lon)
    if mc is None:
        mc = get_mc(t, lon)

    system = system.lower()

    if system == "equal":
        cusps = houses_equal(asc)
    elif system == "whole_sign":
        cusps = houses_whole_sign(asc)
    elif system == "porphyry":
        cusps = houses_porphyry(asc, mc)
    elif system == "placidus":
        cusps = houses_placidus(t, lat, lon, asc, mc)
    elif system == "koch":
        cusps = houses_koch(t, lat, lon, asc, mc)
    elif system == "regiomontanus":
        cusps = houses_regiomontanus(t, lat, lon, asc, mc)
    else:
        raise ValueError(f"سیستم خانه ناشناخته: {system}")

    return {
        "system": system,
        "ASC": asc,
        "MC": mc,
        "cusps": {i+1: cusps[i] for i in range(12)}
    }
