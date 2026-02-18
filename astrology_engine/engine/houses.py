
import numpy as np
from skyfield.api import load

ts = load.timescale()
eph = load('de440.bsp')

def get_mc(t, lon):
    gst = t.gast
    lst = (gst + lon / 15) % 24
    lst_rad = np.radians(lst * 15)
    eps = np.radians(23.4392911)
    mc = np.degrees(np.arctan2(np.sin(lst_rad), np.cos(lst_rad) * np.cos(eps)))
    return mc % 360

def get_ascendant(t, lat, lon):
    gst = t.gast
    lst = (gst + lon / 15) % 24
    lst_rad = np.radians(lst * 15)

    eps = np.radians(23.4392911)
    lat_rad = np.radians(lat)

    tan_asc = -np.cos(lst_rad) / (np.sin(lst_rad) * np.cos(eps) - np.tan(lat_rad) * np.sin(eps))
    asc = np.degrees(np.arctan(tan_asc))

    if np.sin(lst_rad) * np.cos(eps) - np.tan(lat_rad) * np.sin(eps) < 0:
        asc += 180

    return asc % 360

def placidus_houses(t, lat, lon):
    lat_rad = np.radians(lat)
    eps = np.radians(23.4392911)

    mc = get_mc(t, lon)
    asc = get_ascendant(t, lat, lon)

    houses = [0] * 12
    houses[0] = asc
    houses[9] = mc

    mc_rad = np.radians(mc)
    ra_mc = np.arctan2(np.sin(mc_rad) * np.cos(eps), np.cos(mc_rad))

    for i, factor in zip([11, 10, 1, 2], [1/3, 2/3, 4/3, 5/3]):
        ra = ra_mc + factor * np.pi
        lon_house = np.degrees(np.arctan2(
            np.sin(ra),
            np.cos(ra) * np.cos(eps)
        ))
        houses[i] = lon_house % 360

    houses[6] = (houses[0] + 180) % 360
    houses[7] = (houses[1] + 180) % 360
    houses[8] = (houses[2] + 180) % 360
    houses[3] = (houses[9] + 180) % 360
    houses[4] = (houses[10] + 180) % 360
    houses[5] = (houses[11] + 180) % 360

    return houses
