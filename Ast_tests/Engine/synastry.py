#%%writefile Mehrozkiyad/astrology_engine/engine/synastry.py
from .planets import get_all_planets, get_time
from .aspects import detect_inter_aspects

def compute_synastry(
    a_year, a_month, a_day, a_hour, a_minute, a_tz, a_lat, a_lon,
    b_year, b_month, b_day, b_hour, b_minute, b_tz, b_lat, b_lon
):
    # زمان دو چارت
    t_a = get_time(a_year, a_month, a_day, a_hour, a_minute, a_tz)
    t_b = get_time(b_year, b_month, b_day, b_hour, b_minute, b_tz)

    # سیارات دو چارت
    a_planets = get_all_planets(t_a)
    b_planets = get_all_planets(t_b)

    # جنبه‌های بین دو چارت
    inter_aspects = detect_inter_aspects(a_planets, b_planets)

    return {
        "chart_a": a_planets,
        "chart_b": b_planets,
        "inter_aspects": inter_aspects,
    }
