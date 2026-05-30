# aspect_tools.py
# ابزارهای پیشرفتهٔ کار با جنبه‌ها:
# 1) Filtering Engine
# 2) Weight System
# 3) Orb Rules per planet
# 4) Aspect Priority Engine
# 5) Transit Engine
# 6) Progressions Engine

from typing import List, Dict, Optional

# مسیر صحیح مطابق ساختار پروژهٔ تو:
from astrology_core.Engine.planets import (
    get_time,
    get_all_planets,
    get_aspect_engine,
)

Aspect = Dict[str, object]


# =========================================================
# 1) Filtering Engine
# =========================================================

def filter_aspects(
    aspects: List[Aspect],
    categories: Optional[List[str]] = None,
    planets_included: Optional[List[str]] = None,
    planets_excluded: Optional[List[str]] = None,
    max_orb: Optional[float] = None,
    min_orb: Optional[float] = None,
    types_included: Optional[List[str]] = None,
) -> List[Aspect]:

    result = []

    for a in aspects:
        cat = a["category"]
        p1 = a["p1"]
        p2 = a["p2"]
        orb = a["orb"]
        atype = a["type"]

        if categories and cat not in categories:
            continue

        if planets_included and not (p1 in planets_included or p2 in planets_included):
            continue

        if planets_excluded and (p1 in planets_excluded or p2 in planets_excluded):
            continue

        if max_orb is not None and orb > max_orb:
            continue

        if min_orb is not None and orb < min_orb:
            continue

        if types_included and atype not in types_included:
            continue

        result.append(a)

    return result


# =========================================================
# 2) Weight System
# =========================================================

ASPECT_BASE_WEIGHTS = {
    "Conjunction": 5,
    "Opposition": 5,
    "Square": 4,
    "Trine": 4,
    "Sextile": 3,
    "Quincunx": 3,
    "Semi-Sextile": 2,
    "Semi-Square": 2,
    "Sesquiquadrate": 2,
    "Parallel": 4,
    "Contra-Parallel": 4,
    "Lat-Parallel": 3,
    "Lat-Contra-Parallel": 3,
}

PLANET_WEIGHTS = {
    "Sun": 5,
    "Moon": 5,
    "Asc": 5,
    "MC": 5,
    "Mercury": 3,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 3,
    "Saturn": 4,
    "Uranus": 3,
    "Neptune": 3,
    "Pluto": 4,
}


def get_planet_weight(planet: str) -> int:
    return PLANET_WEIGHTS.get(planet, 2)


def compute_aspect_weight(aspect: Aspect, max_orb_for_type: float = 6.0) -> float:

    base = ASPECT_BASE_WEIGHTS.get(aspect["type"], 1)
    p1_w = get_planet_weight(aspect["p1"])
    p2_w = get_planet_weight(aspect["p2"])
    orb = aspect["orb"]

    tight_factor = max(0.1, 1.0 - (orb / max_orb_for_type))

    weight = base * (p1_w + p2_w) / 10.0 * tight_factor
    return round(weight, 3)


def add_weights_to_aspects(aspects: List[Aspect]) -> List[Aspect]:

    for a in aspects:
        if a["category"] == "Longitude":
            max_orb = 6.0
        elif a["category"] == "Declination":
            max_orb = 1.5
        else:
            max_orb = 1.5

        a["weight"] = compute_aspect_weight(a, max_orb_for_type=max_orb)

    return aspects


# =========================================================
# 3) Orb Rules per planet
# =========================================================

PLANET_ORB_FACTORS = {
    "Sun": 1.0,
    "Moon": 1.0,
    "Mercury": 0.8,
    "Venus": 0.8,
    "Mars": 0.9,
    "Jupiter": 0.9,
    "Saturn": 0.9,
    "Uranus": 0.7,
    "Neptune": 0.7,
    "Pluto": 0.7,
}

ASPECT_BASE_ORBS = {
    "Conjunction": 8.0,
    "Opposition": 8.0,
    "Square": 7.0,
    "Trine": 7.0,
    "Sextile": 5.0,
    "Quincunx": 3.0,
    "Semi-Sextile": 2.0,
    "Semi-Square": 2.0,
    "Sesquiquadrate": 2.0,
    "Parallel": 1.5,
    "Contra-Parallel": 1.5,
    "Lat-Parallel": 1.0,
    "Lat-Contra-Parallel": 1.0,
}


def get_orb_for_aspect(atype: str, p1: str, p2: str) -> float:

    base = ASPECT_BASE_ORBS.get(atype, 2.0)
    f1 = PLANET_ORB_FACTORS.get(p1, 0.8)
    f2 = PLANET_ORB_FACTORS.get(p2, 0.8)

    return base * (f1 + f2) / 2.0


# =========================================================
# 4) Aspect Priority Engine
# =========================================================

def sort_aspects_by_priority(aspects: List[Aspect]) -> List[Aspect]:

    def key(a: Aspect):
        w = a.get("weight", 0.0)
        return (-w, a["orb"])

    return sorted(aspects, key=key)


def get_top_aspects(
    aspects: List[Aspect],
    min_weight: float = 0.0,
    max_count: Optional[int] = None
) -> List[Aspect]:

    filtered = [a for a in aspects if a.get("weight", 0.0) >= min_weight]
    sorted_aspects = sort_aspects_by_priority(filtered)

    if max_count is not None:
        return sorted_aspects[:max_count]
    return sorted_aspects


# =========================================================
# 5) Transit Engine
# =========================================================

def get_transit_aspects(
    natal_planets: Dict[str, Dict[str, float]],
    transit_planets: Dict[str, Dict[str, float]],
    orb_lon_major=6.0,
    orb_lon_minor=3.0,
    orb_dec=1.0,
    orb_lat=1.0,
) -> List[Aspect]:

    combined: Dict[str, Dict[str, float]] = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in transit_planets.items():
        combined[f"T_{name}"] = data

    aspects = get_aspect_engine(
        combined,
        orb_lon_major=orb_lon_major,
        orb_lon_minor=orb_lon_minor,
        orb_dec=orb_dec,
        orb_lat=orb_lat,
    )

    result: List[Aspect] = []
    for a in aspects:
        p1 = a["p1"]
        p2 = a["p2"]
        if (p1.startswith("N_") and p2.startswith("T_")) or (p1.startswith("T_") and p2.startswith("N_")):
            result.append(a)

    return result


# =========================================================
# 6) Progressions Engine (Secondary Progressions)
# =========================================================

def get_secondary_progressed_planets(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    target_year: int,
    target_month: int,
    target_day: int,
    target_hour: int,
    target_minute: int,
):

    years_diff = target_year - birth_year

    progressed_t = get_time(
        birth_year,
        birth_month,
        birth_day + years_diff,
        birth_hour,
        birth_minute,
    )

    return get_all_planets(progressed_t)


def get_progressed_aspects_to_natal(
    natal_planets: Dict[str, Dict[str, float]],
    progressed_planets: Dict[str, Dict[str, float]],
    orb_lon_major=6.0,
    orb_lon_minor=3.0,
    orb_dec=1.0,
    orb_lat=1.0,
) -> List[Aspect]:

    combined: Dict[str, Dict[str, float]] = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in progressed_planets.items():
        combined[f"P_{name}"] = data

    aspects = get_aspect_engine(
        combined,
        orb_lon_major=orb_lon_major,
        orb_lon_minor=orb_lon_minor,
        orb_dec=orb_dec,
        orb_lat=orb_lat,
    )

    result: List[Aspect] = []
    for a in aspects:
        p1 = a["p1"]
        p2 = a["p2"]
        if (p1.startswith("N_") and p2.startswith("P_")) or (p1.startswith("P_") and p2.startswith("N_")):
            result.append(a)

    return result
