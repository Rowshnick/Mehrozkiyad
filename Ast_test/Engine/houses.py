from skyfield.api import load, wgs84
import numpy as np

eph = load('de440.bsp')
ts = load.timescale()

def normalize(angle):
    return angle % 360

def get_ascendant(t, lat, lon):
    """
    محاسبهٔ ASC با روش استاندارد Skyfield:
    - تبدیل افق به مختصات استوایی
    - تبدیل استوایی به دایرةالبروجی
    """
    observer = wgs84.latlon(lat, lon)
    astrometric = observer.at(t).from_altaz(alt_degrees=0, az_degrees=90)

    ra, dec, _ = astrometric.radec()

    eps = np.radians(23.4392911)

    ra_rad = ra.radians
    dec_rad = dec.radians

    lon = np.degrees(
        np.arctan2(
            np.sin(ra_rad) * np.cos(eps) + np.tan(dec_rad) * np.sin(eps),
            np.cos(ra_rad)
        )
    ) % 360

    return lon

def get_mc(t, lon):
    """
    MC = RA of meridian converted to ecliptic longitude
    """
    gst = t.gast  # Greenwich Apparent Sidereal Time
    lst = (gst + lon / 15) % 24  # Local Sidereal Time

    ra_mc = lst * 15  # degrees

    eps = np.radians(23.4392911)
    ra_rad = np.radians(ra_mc)

    lon_mc = np.degrees(np.arctan2(np.sin(ra_rad) * np.cos(eps), np.cos(ra_rad))) % 360

    return lon_mc

def placidus_houses(t, lat, lon):
    asc = get_ascendant(t, lat, lon)
    mc = get_mc(t, lon)

    houses = [0] * 12
    houses[0] = asc
    houses[9] = mc

    for i in range(1, 12):
        houses[i] = normalize(asc + i * 30)

    return houses

