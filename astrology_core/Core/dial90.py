# astrology_core/Core/dial90.py
# 90° Dial Engine (Uranian-style ساده)

from .aspects import norm_deg, diff_deg

def to_90(lon: float) -> float:
    return norm_deg(lon) % 90.0

def build_90_points(bodies: dict):
    """
    bodies: dict[name] = {"lon": ...}
    خروجی: dict[name] = {"lon_360": ..., "lon_90": ...}
    """
    out = {}
    for name, data in bodies.items():
        lon = data.get("lon")
        if lon is None:
            continue
        out[name] = {
            "lon_360": norm_deg(lon),
            "lon_90": to_90(lon),
        }
    return out

def find_90_midpoints(points_90: dict, max_orb=1.0):
    """
    midpointهای 90° (harmonic 4) با orb کوچک
    """
    names = list(points_90.keys())
    mids = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            a = points_90[n1]["lon_90"]
            b = points_90[n2]["lon_90"]
            d = diff_deg(a, b)
            if d <= max_orb:
                mids.append({
                    "point1": n1,
                    "point2": n2,
                    "angle_90": (a + b) / 2.0,
                    "orb": d,
                })
    return mids
