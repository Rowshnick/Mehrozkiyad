
import math

ASPECTS = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Quincunx": 150,
    "Opposition": 180,
}

ORB = 6

def angle_diff(a, b):
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff

def detect_aspects(points):
    results = []
    names = list(points.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1 = names[i]
            p2 = names[j]
            lon1 = float(points[p1]["lon"])
            lon2 = float(points[p2]["lon"])
            diff = angle_diff(lon1, lon2)
            for aspect_name, aspect_angle in ASPECTS.items():
                orb = abs(diff - aspect_angle)
                if orb <= ORB:
                    results.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": aspect_name,
                        "orb": orb
                    })
    return results

def detect_inter_aspects(points_transit, points_natal, orb=6):
    results = []
    for t_name, t_val in points_transit.items():
        for n_name, n_val in points_natal.items():
            lon_t = float(t_val["lon"])
            lon_n = float(n_val["lon"])
            diff = angle_diff(lon_t, lon_n)
            for aspect_name, aspect_angle in ASPECTS.items():
                this_orb = abs(diff - aspect_angle)
                if this_orb <= orb:
                    results.append({
                        "transit_point": t_name,
                        "natal_point": n_name,
                        "aspect": aspect_name,
                        "orb": this_orb
                    })
    return results
