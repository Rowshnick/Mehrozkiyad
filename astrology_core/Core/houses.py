# astrology_core/Core/houses.py
# House Engine:
# - محاسبه Asc و MC
# - ساخت خانه‌ها (Equal House از Asc)

import numpy as np

from astrology_core.Engine.planets import ts, eph


def get_asc_mc(t, latitude_deg: float, longitude_deg: float):
    """
    محاسبه Ascendant و Midheaven (MC) بر حسب طول دایرةالبروجی (درجه)
    t: زمان Skyfield (خروجی get_time)
    latitude_deg: عرض جغرافیایی محل (مثلاً 52.37 برای آمستردام)
    longitude_deg: طول جغرافیایی محل (مثلاً 4.90 برای آمستردام، شرق مثبت)
    """

    # تبدیل به رادیان
    phi = np.radians(latitude_deg)          # عرض جغرافیایی
    lon = np.radians(longitude_deg)         # طول جغرافیایی
    eps = np.radians(23.4392911)            # اوبلیکویتی

    # زمان اختری محلی (Local Sidereal Time)
    # t.gast = Greenwich Apparent Sidereal Time (ساعت)
    gast_hours = t.gast
    theta = np.radians(gast_hours * 15.0) + lon  # تبدیل به رادیان و اضافه کردن طول جغرافیایی

    # نرمال‌سازی
    theta = theta % (2 * np.pi)

    # فرمول‌های استاندارد MC و Asc روی دایرةالبروج
    # MC:
    # tan(λ_MC) = (sin(θ) * cos(ε) + tan(φ) * sin(ε)) / cos(θ)
    num_mc = np.sin(theta) * np.cos(eps) + np.tan(phi) * np.sin(eps)
    den_mc = np.cos(theta)
    lam_mc = np.degrees(np.arctan2(num_mc, den_mc)) % 360.0

    # Asc:
    # tan(λ_ASC) = -cos(θ) / (sin(θ)*cos(ε) - tan(φ)*sin(ε))
    num_asc = -np.cos(theta)
    den_asc = np.sin(theta) * np.cos(eps) - np.tan(phi) * np.sin(eps)
    lam_asc = np.degrees(np.arctan2(num_asc, den_asc)) % 360.0

    return lam_asc, lam_mc


def build_equal_houses(asc_lon: float):
    """
    ساخت خانه‌ها به روش Equal House از Asc:
    - خانه ۱ از Asc شروع می‌شود
    - هر خانه ۳۰ درجه
    خروجی: لیست ۱۲تایی طول شروع هر خانه
    """

    houses = []
    for i in range(12):
        h = (asc_lon + i * 30.0) % 360.0
        houses.append(h)
    return houses


def get_house_index(point_lon: float, houses: list):
    """
    تعیین شمارهٔ خانه برای یک نقطه (طول دایرةالبروجی) بر اساس
    خانه‌های Equal House.
    خروجی: عدد 1 تا 12
    """

    # فرض: houses = شروع هر خانه، به ترتیب از خانه ۱ تا ۱۲
    for i in range(12):
        start = houses[i]
        end = houses[(i + 1) % 12]

        if start < end:
            if start <= point_lon < end:
                return i + 1
        else:
            # عبور از 360
            if point_lon >= start or point_lon < end:
                return i + 1

    return None  # نباید برسیم اینجا، ولی برای اطمینان


def assign_planets_to_houses(planets: dict, houses: list):
    """
    نسبت دادن سیارات به خانه‌ها بر اساس طول دایرةالبروجی‌شان.
    planets: خروجی get_all_planets
    houses: خروجی build_equal_houses
    خروجی: دیکشنری {planet_name: house_number}
    """

    result = {}
    for name, data in planets.items():
        lon = data["lon"]
        h = get_house_index(lon, houses)
        result[name] = h
    return result
