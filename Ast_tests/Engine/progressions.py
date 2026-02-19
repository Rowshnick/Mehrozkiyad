#%%writefile Mehrozkiyad/astrology_engine/engine/progressions.py
from .planets import get_all_planets, get_time, ts
from .aspects import detect_inter_aspects

def progressed_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz, age_years):
    # زمان تولد
    t0 = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)

    # 1 سال = 1 روز → پس age_years روز به زمان تولد اضافه می‌کنیم
    jd_progressed = t0.tt + age_years

    # تبدیل دوباره به Time object
    return ts.tt_jd(jd_progressed)

def compute_secondary_progressions(
    natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz,
    natal_lat, natal_lon,
    age_years
):
    # زمان ناتال
    t_natal = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)

    # زمان پروگرس‌شده دقیق
    t_prog = progressed_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz, age_years)

    # سیارات ناتال و پروگرس‌شده
    natal_planets = get_all_planets(t_natal)
    prog_planets = get_all_planets(t_prog)

    # جنبه‌های پروگرس‌شده → ناتال
    inter_aspects = detect_inter_aspects(prog_planets, natal_planets)

    return {
        "natal_planets": natal_planets,
        "progressed_planets": prog_planets,
        "inter_aspects": inter_aspects,
        "progressed_time": t_prog.tt,
    }
