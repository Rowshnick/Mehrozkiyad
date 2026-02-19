#%%writefile Mehrozkiyad/astrology_engine/engine/aspects.py
import itertools
import numpy as np

ASPECTS = {
    "conjunction": 0.0,
    "opposition": 180.0,
    "trine": 120.0,
    "square": 90.0,
    "sextile": 60.0,
}

ORB = 6.0  # درجه

def _angle_diff(a, b):
    diff = (a - b + 540.0) % 360.0 - 180.0
    return abs(diff)

def _detect_between_two(lon1, lon2):
    results = []
    angle = _angle_diff(lon1, lon2)
    for name, exact in ASPECTS.items():
        orb = abs(angle - exact)
        if orb <= ORB:
            results.append((name, angle, orb))
    return results

def detect_aspects(points):
    """
    points: dict مثل {"Sun": {"lon": ...}, "Moon": {...}, ...}
    """
    aspects = []
    keys = list(points.keys())
    for a, b in itertools.combinations(keys, 2):
        lon1 = points[a]["lon"]
        lon2 = points[b]["lon"]
        hits = _detect_between_two(lon1, lon2)
        for name, angle, orb in hits:
            aspects.append({
                "p1": a,
                "p2": b,
                "type": name,
                "angle": float(angle),
                "orb": float(orb),
            })
    return aspects

def detect_inter_aspects(points_a, points_b):
    """
    جنبه‌ها بین دو مجموعه نقاط:
    points_a: dict
    points_b: dict
    """
    aspects = []
    for name_a, pa in points_a.items():
        for name_b, pb in points_b.items():
            lon1 = pa["lon"]
            lon2 = pb["lon"]
            hits = _detect_between_two(lon1, lon2)
            for name, angle, orb in hits:
                aspects.append({
                    "p1": name_a,
                    "p2": name_b,
                    "type": name,
                    "angle": float(angle),
                    "orb": float(orb),
                })
    return aspects
