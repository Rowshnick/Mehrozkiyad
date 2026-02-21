# astrology_core/Core/aspects.py
# Aspect Engine حرفه‌ای (Planet/Point/House)

import math

# -------------------------
# ابزارهای کمکی
# -------------------------

def norm_deg(a: float) -> float:
    return a % 360.0

def diff_deg(a: float, b: float) -> float:
    d = abs(norm_deg(a - b))
    return d if d <= 180.0 else 360.0 - d

# -------------------------
# تعریف جنبه‌ها
# -------------------------

ASPECT_DEFS = {
    "conjunction":  {"angle": 0.0,   "type": "major", "base_orb": 10.0, "weight": 1.00},
    "opposition":   {"angle": 180.0, "type": "major", "base_orb": 10.0, "weight": 0.95},
    "trine":        {"angle": 120.0, "type": "major", "base_orb": 8.0,  "weight": 0.90},
    "square":       {"angle": 90.0,  "type": "major", "base_orb": 8.0,  "weight": 0.90},
    "sextile":      {"angle": 60.0,  "type": "major", "base_orb": 6.0,  "weight": 0.75},

    "quincunx":     {"angle": 150.0, "type": "minor", "base_orb": 3.0,  "weight": 0.50},
    "semisextile":  {"angle": 30.0,  "type": "minor", "base_orb": 2.0,  "weight": 0.40},
    "semisquare":   {"angle": 45.0,  "type": "minor", "base_orb": 2.0,  "weight": 0.45},
    "sesquiquadrate":{"angle":135.0, "type": "minor", "base_orb": 2.0,  "weight": 0.45},
    "quintile":     {"angle": 72.0,  "type": "minor", "base_orb": 2.0,  "weight": 0.40},
    "biquintile":   {"angle":144.0,  "type": "minor", "base_orb": 2.0,  "weight": 0.40},
    "septile":      {"angle":51.428, "type": "minor", "base_orb": 1.5,  "weight": 0.35},
    "biseptile":    {"angle":102.857,"type": "minor", "base_orb": 1.5,  "weight": 0.35},
    "triseptile":   {"angle":154.285,"type": "minor", "base_orb": 1.5,  "weight": 0.35},
    "novile":       {"angle":40.0,   "type": "minor", "base_orb": 1.5,  "weight": 0.35},
    "decile":       {"angle":36.0,   "type": "minor", "base_orb": 1.5,  "weight": 0.35},
    "undecile":     {"angle":32.727, "type": "minor", "base_orb": 1.0,  "weight": 0.30},
    "vigintile":    {"angle":18.0,   "type": "minor", "base_orb": 1.0,  "weight": 0.30},
}

# -------------------------
# وزن سیارات / نقاط
# -------------------------

def classify_body(name: str):
    n = name.lower()
    if n in ["sun", "moon"]:
        return "luminary"
    if n in ["mercury", "venus", "mars"]:
        return "personal"
    if n in ["jupiter", "saturn"]:
        return "social"
    if n in ["uranus", "neptune", "pluto"]:
        return "transpersonal"
    if n in ["chiron", "ceres", "pallas", "juno", "vesta"]:
        return "asteroid"
    if n in ["asc", "mc", "ic", "dsc", "node", "north node", "south node",
             "lilith", "fortune", "vertex", "east point", "equatorial asc"]:
        return "angle"
    if n.startswith("cusp"):
        return "cusp"
    if "/" in n:
        return "midpoint"
    return "other"

def planet_weight(name: str) -> float:
    t = classify_body(name)
    if t == "luminary":
        return 1.0
    if t == "personal":
        return 0.9
    if t == "social":
        return 0.8
    if t == "transpersonal":
        return 0.7
    if t == "asteroid":
        return 0.4
    if t in ["angle", "cusp"]:
        return 0.6
    if t == "midpoint":
        return 0.7
    return 0.5

def adjust_orb_for_body(base_orb: float, name1: str, name2: str) -> float:
    # ساده ولی پویا: بر اساس نوع دو نقطه
    w1 = planet_weight(name1)
    w2 = planet_weight(name2)
    avg = (w1 + w2) / 2.0
    # luminary → orb بزرگ‌تر، asteroid → کوچک‌تر
    return base_orb * (0.7 + 0.6 * avg)

# -------------------------
# applying / separating
# -------------------------

def is_applying(lon1, lon2, speed1=None, speed2=None, exact_angle=0.0):
    """
    اگر سرعت‌ها موجود باشند، از آن‌ها استفاده می‌کند؛
    در غیر این صورت، None برمی‌گرداند.
    """
    if speed1 is None or speed2 is None:
        return None

    # سیارهٔ سریع‌تر
    if abs(speed1) >= abs(speed2):
        fast_lon, fast_speed = lon1, speed1
        slow_lon = lon2
    else:
        fast_lon, fast_speed = lon2, speed2
        slow_lon = lon1

    # زاویهٔ فعلی
    current = diff_deg(fast_lon, slow_lon)
    # اگر fast در حال نزدیک شدن به exact_angle باشد → applying
    # تقریب: نگاه به جهت حرکت fast نسبت به slow
    future = diff_deg(fast_lon + fast_speed * 0.01, slow_lon)
    if abs(future - exact_angle) < abs(current - exact_angle):
        return True
    else:
        return False

# -------------------------
# محاسبهٔ جنبه بین دو نقطه
# -------------------------

def compute_aspect_between(name1, lon1, name2, lon2, speed1=None, speed2=None,
                           allowed_aspects=None, max_orb_scale=1.0):
    if allowed_aspects is None:
        allowed_aspects = list(ASPECT_DEFS.keys())

    angle = diff_deg(lon1, lon2)

    best = None
    for asp_name in allowed_aspects:
        asp_def = ASPECT_DEFS[asp_name]
        exact = asp_def["angle"]
        base_orb = asp_def["base_orb"] * max_orb_scale
        orb_max = adjust_orb_for_body(base_orb, name1, name2)

        orb = abs(angle - exact)
        if orb <= orb_max:
            # نزدیک‌ترین جنبه
            if (best is None) or (orb < best["orb"]):
                applying_flag = is_applying(lon1, lon2, speed1, speed2, exact_angle=exact)
                w_asp = asp_def["weight"]
                w_pl = (planet_weight(name1) + planet_weight(name2)) / 2.0
                strength = w_asp * w_pl * (1.0 - orb / orb_max)
                if applying_flag is True:
                    strength *= 1.1
                elif applying_flag is False:
                    strength *= 0.9

                best = {
                    "planet1": name1,
                    "planet2": name2,
                    "aspect": asp_name,
                    "angle": angle,
                    "orb": orb,
                    "max_orb": orb_max,
                    "type": asp_def["type"],
                    "applying": applying_flag,
                    "strength": strength,
                }

    return best

# -------------------------
# محاسبهٔ جنبه برای همهٔ نقاط
# -------------------------

def compute_all_aspects(bodies: dict, allowed_aspects=None, max_orb_scale=1.0):
    """
    bodies: dict[name] = {"lon": ..., "speed": optional}
    """
    names = list(bodies.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            d1, d2 = bodies[n1], bodies[n2]
            lon1 = d1.get("lon")
            lon2 = d2.get("lon")
            if lon1 is None or lon2 is None:
                continue
            sp1 = d1.get("speed")
            sp2 = d2.get("speed")

            asp = compute_aspect_between(
                n1, lon1, n2, lon2, sp1, sp2,
                allowed_aspects=allowed_aspects,
                max_orb_scale=max_orb_scale,
            )
            if asp is not None:
                aspects.append(asp)

    return aspects
