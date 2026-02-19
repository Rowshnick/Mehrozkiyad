from skyfield.api import load, wgs84
import numpy as np

eph = load('de440.bsp')
ts = load.timescale()

def normalize(angle):
    return angle % 360

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

# ---------- سیستم‌های مختلف خانه ----------

def houses_equal(asc):
    cusps = []
    for i in range(12):
        cusps.append(normalize(asc + i * 30))
    return cusps

def houses_whole_sign(asc):
    sign_start = int(asc // 30) * 30
    cusps = []
    for i in range(12):
        cusps.append(normalize(sign_start + i * 30))
    return cusps

def houses_porphyry(asc, mc):
    # Porphyry: تقسیم قوس بین ASC و MC و بین MC و DSC به سه قسمت مساوی
    dsc = normalize(asc + 180)
    ic = normalize(mc + 180)

    def divide_arc(start, end):
        arc = (end - start) % 360
        return [normalize(start + arc * i / 3) for i in range(3)]

    # 1–4–7–10
    c1 = asc
    c10 = mc
    c7 = dsc
    c4 = ic

    # بین 1 و 10 → خانه‌های 12 و 11
    seg_1_10 = divide_arc(c1, c10)
    # بین 10 و 7 → خانه‌های 9 و 8
    seg_10_7 = divide_arc(c10, c7)
    # بین 7 و 4 → خانه‌های 6 و 5
    seg_7_4 = divide_arc(c7, c4)
    # بین 4 و 1 → خانه‌های 3 و 2
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

# ---------- رابط اصلی ----------

def compute_houses(t, lat, lon, system="placidus", asc=None, mc=None):
    """
    system: "equal", "whole_sign", "porphyry", "placidus", "koch", "regiomontanus"
    (فعلاً equal / whole_sign / porphyry پیاده شده‌اند)
    """
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
    elif system in ("placidus", "koch", "regiomontanus"):
        # جای خالی برای پیاده‌سازی دقیق
        raise NotImplementedError(f"House system '{system}' هنوز پیاده‌سازی نشده است.")
    else:
        raise ValueError(f"سیستم خانه ناشناخته: {system}")

    return {
        "system": system,
        "ASC": asc,
        "MC": mc,
        "cusps": {i+1: cusps[i] for i in range(12)}
    }
