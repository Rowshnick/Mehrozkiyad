# points.py 

import numpy as np

def normalize(angle):
    """نرمال‌سازی زاویه به بازه ۰ تا ۳۶۰ درجه"""
    return angle % 360

def get_extra_points(t, lat, lon, asc, sun_lon, moon_lon):
    """
    محاسبهٔ نقاط اضافی:
    - Midheaven (MC)
    - Vertex
    - Part of Fortune (POF)
    """

    points = {}

    # MC ساده (اگر از houses.py استفاده نشود)
    mc = normalize(asc + 90)
    points["MC"] = {"lon": mc, "lat": 0}

    # Vertex
    vertex = normalize(asc + 180)
    points["Vertex"] = {"lon": vertex, "lat": 0}

    # Part of Fortune
    pof = normalize(asc + moon_lon - sun_lon)
    points["POF"] = {"lon": pof, "lat": 0}

    return points
