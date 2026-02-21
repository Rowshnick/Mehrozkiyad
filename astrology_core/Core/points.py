# astrology_core/Core/points.py
# نسخهٔ هماهنگ با chart_engine.py جدید

import numpy as np

def norm_deg(a):
    return a % 360.0

def get_extra_points(t, asc, mc, latitude_deg, longitude_deg, planets=None):
    """
    نسخهٔ جدید: moon_lon را از دیکشنری planets می‌گیرد.
    chart_engine.py این دیکشنری را ارسال می‌کند.
    """

    if planets is None:
        raise ValueError("points.py: دیکشنری سیارات ارسال نشده است.")

    if "Moon" not in planets:
        raise ValueError("points.py: سیاره Moon در دیکشنری وجود ندارد.")

    moon_lon = planets["Moon"]["lon"]
    sun_lon  = planets["Sun"]["lon"]

    # -------------------------
    # Node (True Node ساده)
    # -------------------------
    node = norm_deg(moon_lon + 180.0)

    # -------------------------
    # Lilith (Mean Black Moon)
    # -------------------------
    lilith = norm_deg(moon_lon - 180.0)

    # -------------------------
    # Part of Fortune
    # -------------------------
    # فرمول ناتال (روز):
    fortune = norm_deg(asc + moon_lon - sun_lon)

    # -------------------------
    # Vertex (تقریب استاندارد)
    # -------------------------
    # فرمول ساده‌شده: Vertex = Asc + (MC - Asc)/2
    vertex = norm_deg(asc + (mc - asc) / 2.0)

    # -------------------------
    # East Point
    # -------------------------
    east_point = norm_deg(mc + 90.0)

    return {
        "Node": {"lon": node},
        "Lilith": {"lon": lilith},
        "Fortune": {"lon": fortune},
        "Vertex": {"lon": vertex},
        "East Point": {"lon": east_point},
    }
