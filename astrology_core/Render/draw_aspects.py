============================================================

DRAW_ASPECTS (THEME-DRIVEN VERSION)

Fully rewritten by Roshina Project

============================================================

from .chart_renderer import chart_angle
from .theme import get_theme

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


def normalize_aspects(aspects_raw):
    if isinstance(aspects_raw, list):
        return {"planet_aspects": aspects_raw}
    if isinstance(aspects_raw, dict):
        return aspects_raw
    return {"planet_aspects": []}


def draw_aspects(ax, chart, r_planets=0.70, theme_name="dark", show_aspects=True):
    if not show_aspects:
        return

    theme = get_theme(theme_name)
    planets = chart.get("planets", {})
    aspects = normalize_aspects(chart.get("aspects"))

    for asp in aspects.get("planet_aspects", []):
        a_type = asp.get("aspect")
        if a_type not in MAJOR_ASPECTS:
            continue

        p1 = asp.get("planet1")
        p2 = asp.get("planet2")
        if p1 not in planets or p2 not in planets:
            continue

        lon1 = planets[p1]["lon"]
        lon2 = planets[p2]["lon"]

        theta1 = chart_angle(lon1)
        theta2 = chart_angle(lon2)

        color = theme["aspect_colors"].get(a_type, "#888888")
        strength = asp.get("strength", 0.5)
        lw = 0.5 + 2.0 * max(0.0, min(1.0, strength))

        ax.plot(
            [theta1, theta2],
            [r_planets, r_planets],
            color=color,
            linewidth=lw,
            alpha=theme["aspect_line_alpha"],
            zorder=3,
        )
