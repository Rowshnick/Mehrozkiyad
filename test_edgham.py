from astrology_core.Engine.planets import get_time, get_all_planets
from astrology_core.Core.aspect_tools import (
    add_weights_to_aspects,
    get_top_aspects,
)

t = get_time(1990, 1, 1, 12, 0, 0)
planets = get_all_planets(t)

print("Planets OK, count:", len(planets))

from astrology_core.Engine.planets import get_aspect_engine
aspects = get_aspect_engine(planets)

print("Aspects OK, count:", len(aspects))

add_weights_to_aspects(aspects)
top = get_top_aspects(aspects, min_weight=2.0, max_count=10)

print("Top aspects:")
for a in top:
    print(a)
