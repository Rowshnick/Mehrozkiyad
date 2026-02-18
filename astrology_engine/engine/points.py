
import numpy as np
from skyfield.api import load

ts = load.timescale()
eph = load('de440.bsp')

def get_true_node(t):
    jd = t.tt
    T = (jd - 2451545.0) / 36525.0
    mean_long = 125.04452 - 1934.136261 * T + 0.0020708 * T**2 + (T**3) / 450000
    true_node = mean_long % 360
    south_node = (true_node + 180) % 360
    return float(true_node), float(south_node)

def get_chiron(t):
    return float(0.0)

def get_vertex(t, lat, lon):
    gst = t.gast
    lst = (gst + lon / 15) % 24
    lst_rad = np.radians(lst * 15)
    eps = np.radians(23.4392911)
    lat_rad = np.radians(lat)
    tan_vertex = -np.cos(lst_rad) / (np.sin(lst_rad) * np.sin(eps) + np.tan(lat_rad) * np.cos(eps))
    vertex = np.degrees(np.arctan(tan_vertex))
    if np.sin(lst_rad) * np.sin(eps) + np.tan(lat_rad) * np.cos(eps) < 0:
        vertex += 180
    return float(vertex % 360)

def get_part_of_fortune(asc, sun_lon, moon_lon, is_day_chart):
    if is_day_chart:
        pof = asc + moon_lon - sun_lon
    else:
        pof = asc + sun_lon - moon_lon
    return float(pof % 360)

def get_extra_points(t, lat, lon, asc, sun_lon, moon_lon):
    true_node, south_node = get_true_node(t)
    chiron = get_chiron(t)
    vertex = get_vertex(t, lat, lon)
    is_day_chart = ((sun_lon - asc) % 360) < 180
    pof = get_part_of_fortune(asc, sun_lon, moon_lon, is_day_chart)
    return {
        "TrueNode": {"lon": true_node, "lat": 0.0},
        "SouthNode": {"lon": south_node, "lat": 0.0},
        "Chiron": {"lon": chiron, "lat": 0.0},
        "Vertex": {"lon": vertex, "lat": 0.0},
        "PartOfFortune": {"lon": pof, "lat": 0.0},
    }
