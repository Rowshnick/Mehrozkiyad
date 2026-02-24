# astrology_core/Render/angle_utils.py

import math

def deg_to_rad(deg):
    return math.radians(deg)

def chart_angle(lon):
    return deg_to_rad(90 - lon)
