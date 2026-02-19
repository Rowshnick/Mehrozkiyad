#%%writefile Mehrozkiyad/astrology_engine/engine/composite.py
from .planets import get_all_planets, get_time, ts
from .houses import placidus_houses, get_ascendant, get_mc
from .points import get_extra_points
from .aspects import detect_aspects

def _mean_longitude(lon1, lon2):
    diff = (lon2 - lon1 + 540) % 360 - 180
    return (lon1 + diff / 2) % 360

def compute_midpoint_composite(
    a_year, a_month, a_day, a_hour, a_minute, a_tz, a_lat, a_lon,
    b_year, b_month, b_day, b_hour, b_minute, b_tz, b_lat, b_lon
):
    t_a = get_time(a_year, a_month, a_day, a_hour, a_minute, a_tz)
    t_b = get_time(b_year, b_month, b_day, b_hour, b_minute, b_tz)

    a_planets = get_all_planets(t_a)
    b_planets = get_all_planets(t_b)

    composite_planets = {}
    for name in a_planets.keys():
        lon = _mean_longitude(a_planets[name]["lon"], b_planets[name]["lon"])
        lat = (a_planets[name]["lat"] + b_planets[name]["lat"]) / 2
        composite_planets[name] = {"lon": lon, "lat": lat}

    mid_lat = (a_lat + b_lat) / 2
    mid_lon = (a_lon + b_lon) / 2

    t_comp = ts.tt_jd((t_a.tt + t_b.tt) / 2)

    asc = get_ascendant(t_comp, mid_lat, mid_lon)
    mc = get_mc(t_comp, mid_lon)
    houses = placidus_houses(t_comp, mid_lat, mid_lon)

    sun_lon = composite_planets["Sun"]["lon"]
    moon_lon = composite_planets["Moon"]["lon"]
    extra = get_extra_points(t_comp, mid_lat, mid_lon, asc, sun_lon, moon_lon)

    all_points = {**composite_planets, **extra}
    aspects = detect_aspects(all_points)

    return {
        "type": "midpoint",
        "time": t_comp.tt,
        "planets": composite_planets,
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "extra_points": extra,
        "aspects": aspects,
    }

def compute_davison_composite(
    a_year, a_month, a_day, a_hour, a_minute, a_tz, a_lat, a_lon,
    b_year, b_month, b_day, b_hour, b_minute, b_tz, b_lat, b_lon
):
    t_a = get_time(a_year, a_month, a_day, a_hour, a_minute, a_tz)
    t_b = get_time(b_year, b_month, b_day, b_hour, b_minute, b_tz)

    mid_tt = (t_a.tt + t_b.tt) / 2
    t_dav = ts.tt_jd(mid_tt)

    mid_lat = (a_lat + b_lat) / 2
    mid_lon = (a_lon + b_lon) / 2

    planets = get_all_planets(t_dav)
    asc = get_ascendant(t_dav, mid_lat, mid_lon)
    mc = get_mc(t_dav, mid_lon)
    houses = placidus_houses(t_dav, mid_lat, mid_lon)

    sun_lon = planets["Sun"]["lon"]
    moon_lon = planets["Moon"]["lon"]
    extra = get_extra_points(t_dav, mid_lat, mid_lon, asc, sun_lon, moon_lon)

    all_points = {**planets, **extra}
    aspects = detect_aspects(all_points)

    return {
        "type": "davison",
        "time": t_dav.tt,
        "planets": planets,
        "ascendant": asc,
        "midheaven": mc,
        "houses": houses,
        "extra_points": extra,
        "aspects": aspects,
    }
