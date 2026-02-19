#%%writefile Mehrozkiyad/astrology_engine/engine/houses.py
import numpy as np
from .planets import ts

# ثابت اوبلیکویتی (میل محور زمین)
EPSILON = np.radians(23.4392911)

def _julian_day_from_tt(tt):
    # tt در Skyfield خودش Julian Day است
    return tt

def _local_sidereal_time_deg(t, lon_deg):
    jd = _julian_day_from_tt(t.tt)
    T = (jd - 2451545.0) / 36525.0

    GMST = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * T**2
        - (T**3) / 38710000.0
    )
    LST = (GMST + lon_deg) % 360.0
    return LST

def get_mc(t, lon_deg):
    lst = np.radians(_local_sidereal_time_deg(t, lon_deg))
    eps = EPSILON

    # فرمول MC روی دایرةالبروج
    tan_mc = np.tan(lst) * (1.0 / np.cos(eps))
    lon_mc = np.degrees(np.arctan(tan_mc)) % 360.0
    return float(lon_mc)

def get_ascendant(t, lat_deg, lon_deg):
    phi = np.radians(lat_deg)
    lst = np.radians(_local_sidereal_time_deg(t, lon_deg))
    eps = EPSILON

    # فرمول تقریبی طول دایرةالبروجی ASC
    sin_eps = np.sin(eps)
    cos_eps = np.cos(eps)
    sin_lst = np.sin(lst)
    cos_lst = np.cos(lst)
    tan_phi = np.tan(phi)

    numerator = -cos_lst
    denominator = sin_lst * cos_eps - tan_phi * sin_eps

    asc_rad = np.arctan2(numerator, denominator)
    asc_deg = np.degrees(asc_rad) % 360.0
    return float(asc_deg)

def placidus_houses(t, lat_deg, lon_deg):
    """
    برای سادگی فعلاً از سیستم «خانه‌های مساوی از ASC» استفاده می‌کنیم،
    اما تابع را placidus_houses می‌نامیم تا با بقیهٔ کد سازگار بماند.
    """
    asc = get_ascendant(t, lat_deg, lon_deg)
    houses = []
    for i in range(12):
        cusp = (asc + i * 30.0) % 360.0
        houses.append(float(cusp))
    return houses
