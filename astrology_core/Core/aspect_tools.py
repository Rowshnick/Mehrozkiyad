# aspect_tools.py
# ابزارهای پیشرفتهٔ کار با جنبه‌ها:
# 1) Filtering Engine
# 2) Weight System
# 3) Orb Rules per planet
# 4) Aspect Priority Engine
# 5) Transit Engine
# 6) Progressions Engine

from typing import List, Dict, Optional

# موتور جدید جنبه‌ها
from astrology_core.Core.aspects import compute_all_aspects

# موتور سیارات
from astrology_core.Engine.planets import (
    get_time,
    get_all_planets,
)

Aspect = Dict[str, object]


# =========================================================
# 1) Filtering Engine
# =========================================================

def filter_aspects(
    aspects: List[Aspect],
    planets_included: Optional[List[str]] = None,
    planets_excluded: Optional[List[str]] = None,
    max_orb: Optional[float] = None,
    min_orb: Optional[float] = None,
    types_included: Optional[List[str]] = None,
) -> List[Aspect]:

    result = []

    for a in aspects:
        p1 = a["planet1"]
        p2 = a["planet2"]
        orb = a["orb"]
        atype = a["aspect"]

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
    "conjunction": 5,
    "opposition": 5,
    "square": 4,
    "trine": 4,
    "sextile": 3,
    "quincunx": 3,
    "semisextile": 2,
    "semisquare": 2,
    "sesquiquadrate": 2,
    "parallel": 4,
    "contraparallel": 4,
    "latparallel": 3,
    "latcontraparallel": 3,
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

    base = ASPECT_BASE_WEIGHTS.get(aspect["aspect"].lower(), 1)
    p1_w = get_planet_weight(aspect["planet1"])
    p2_w = get_planet_weight(aspect["planet2"])
    orb = aspect["orb"]

    tight_factor = max(0.1, 1.0 - (orb / max_orb_for_type))

    weight = base * (p1_w + p2_w) / 10.0 * tight_factor
    return round(weight, 3)


def add_weights_to_aspects(aspects: List[Aspect]) -> List[Aspect]:

    for a in aspects:
        a["weight"] = compute_aspect_weight(a)

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
    "conjunction": 8.0,
    "opposition": 8.0,
    "square": 7.0,
    "trine": 7.0,
    "sextile": 5.0,
    "quincunx": 3.0,
    "semisextile": 2.0,
    "semisquare": 2.0,
    "sesquiquadrate": 2.0,
    "parallel": 1.5,
    "contraparallel": 1.5,
    "latparallel": 1.0,
    "latcontraparallel": 1.0,
}


def get_orb_for_aspect(atype: str, p1: str, p2: str) -> float:

    base = ASPECT_BASE_ORBS.get(atype.lower(), 2.0)
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
# 5) Transit Engine (updated)
# =========================================================

def get_transit_aspects(
    natal_planets: Dict[str, Dict[str, float]],
    transit_planets: Dict[str, Dict[str, float]],
) -> List[Aspect]:

    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in transit_planets.items():
        combined[f"T_{name}"] = data

    aspects = compute_all_aspects(combined)

    result = []
    for a in aspects:
        p1 = a["planet1"]
        p2 = a["planet2"]
        if (p1.startswith("N_") and p2.startswith("T_")) or (p1.startswith("T_") and p2.startswith("N_")):
            result.append(a)

    return result


# =========================================================
# 6) Progressions Engine (updated)
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
) -> List[Aspect]:

    combined = {}

    for name, data in natal_planets.items():
        combined[f"N_{name}"] = data

    for name, data in progressed_planets.items():
        combined[f"P_{name}"] = data

    aspects = compute_all_aspects(combined)

    result = []
    for a in aspects:
        p1 = a["planet1"]
        p2 = a["planet2"]
        if (p1.startswith("N_") and p2.startswith("P_")) or (p1.startswith("P_") and p2.startswith("N_")):
            result.append(a)

    return result
