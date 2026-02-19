from engine.planets import get_time, get_all_planets

t = get_time(1995, 5, 12, 14, 30, tz_offset=3.5)
planets = get_all_planets(t)

for p, pos in planets.items():
    print(p, pos)
