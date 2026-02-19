#%%writefile Mehrozkiyad/astrology_engine/engine/transits.py
from .planets import get_all_planets, get_time
from .aspects import detect_inter_aspects

def compute_transits_to_natal(
    natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz,
    natal_lat, natal_lon,
    transit_year, transit_month, transit_day, transit_hour, transit_minute, transit_tz
):
    t_natal = get_time(natal_year, natal_month, natal_day, natal_hour, natal_minute, natal_tz)
    t_transit = get_time(transit_year, transit_month, transit_day, transit_hour, transit_minute, transit_tz)

    natal_planets = get_all_planets(t_natal)
    transit_planets = get_all_planets(t_transit)

    inter_aspects = detect_inter_aspects(transit_planets, natal_planets)

    return {
        "natal_planets": natal_planets,
        "transit_planets": transit_planets,
        "inter_aspects": inter_aspects,
    }
