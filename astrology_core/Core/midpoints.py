# astrology_core/Core/midpoints.py
# Midpoint Engine (سطح ۳)

from .aspects import norm_deg, diff_deg, compute_aspect_between

def midpoint_angle(a: float, b: float) -> float:
    a = norm_deg(a)
    b = norm_deg(b)
    d = diff_deg(a, b)
    # جهت کوتاه‌تر
    if ((b - a) % 360.0) <= 180.0:
        m = a + d / 2.0
    else:
        m = a - d / 2.0
    return norm_deg(m)

def build_midpoints(bodies: dict, pairs: list = None):
    """
    bodies: dict[name] = {"lon": ...}
    pairs: لیست جفت‌ها، مثلاً [("Sun","Moon"), ("Venus","Mars"), ...]
    اگر None باشد، همهٔ ترکیب‌های دو‌تایی ساخته می‌شود (سنگین است).
    """
    names = list(bodies.keys())
    midpoints = {}

    if pairs is None:
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                lon1 = bodies[n1].get("lon")
                lon2 = bodies[n2].get("lon")
                if lon1 is None or lon2 is None:
                    continue
                m = midpoint_angle(lon1, lon2)
                key = f"{n1}/{n2}"
                midpoints[key] = {"lon": m}
    else:
        for n1, n2 in pairs:
            if n1 not in bodies or n2 not in bodies:
                continue
            lon1 = bodies[n1].get("lon")
            lon2 = bodies[n2].get("lon")
            if lon1 is None or lon2 is None:
                continue
            m = midpoint_angle(lon1, lon2)
            key = f"{n1}/{n2}"
            midpoints[key] = {"lon": m}

    return midpoints

def compute_midpoint_aspects(midpoints: dict, targets: dict,
                             allowed_aspects=None, max_orb_scale=1.0):
    """
    midpoints: dict[name] = {"lon": ...}
    targets: dict[name] = {"lon": ..., "speed": optional}
    """
    aspects = []
    for m_name, m_data in midpoints.items():
        m_lon = m_data.get("lon")
        if m_lon is None:
            continue
        for t_name, t_data in targets.items():
            t_lon = t_data.get("lon")
            if t_lon is None:
                continue
            sp = t_data.get("speed")
            asp = compute_aspect_between(
                m_name, m_lon, t_name, t_lon,
                speed1=None, speed2=sp,
                allowed_aspects=allowed_aspects,
                max_orb_scale=max_orb_scale,
            )
            if asp is not None:
                aspects.append(asp)
    return aspects

def compute_midpoint_to_midpoint_aspects(midpoints: dict,
                                         allowed_aspects=None,
                                         max_orb_scale=1.0):
    names = list(midpoints.keys())
    aspects = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            lon1 = midpoints[n1].get("lon")
            lon2 = midpoints[n2].get("lon")
            if lon1 is None or lon2 is None:
                continue
            asp = compute_aspect_between(
                n1, lon1, n2, lon2,
                speed1=None, speed2=None,
                allowed_aspects=allowed_aspects,
                max_orb_scale=max_orb_scale,
            )
            if asp is not None:
                aspects.append(asp)
    return aspects
