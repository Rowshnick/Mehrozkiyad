#%%writefile Mehrozkiyad/astrology_engine/engine/points.py
import numpy as np

def get_extra_points(t, lat_deg, lon_deg, asc_deg, sun_lon, moon_lon):
    """
    محاسبهٔ چند نقطهٔ نمادین:
    - گره شمالی و جنوبی (تقریبی)
    - Part of Fortune
    - Vertex (تقریبی)
    """

    # گره شمالی (تقریبی: مقابل مسیر ماه)
    north_node = (moon_lon + 180.0) % 360.0
    south_node = (north_node + 180.0) % 360.0

    # Part of Fortune (فرمول روزانه)
    part_of_fortune = (asc_deg + moon_lon - sun_lon) % 360.0

    # Vertex (تقریبی: ۹۰ درجه از ASC)
    vertex = (asc_deg + 90.0) % 360.0

    points = {
        "North Node": {"lon": float(north_node), "lat": 0.0},
        "South Node": {"lon": float(south_node), "lat": 0.0},
        "Part of Fortune": {"lon": float(part_of_fortune), "lat": 0.0},
        "Vertex": {"lon": float(vertex), "lat": 0.0},
    }

    return points
