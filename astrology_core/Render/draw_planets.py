#============================================================
#DRAW_PLANETS (THEME-DRIVEN VERSION)
#Fully rewritten by Roshina Project
#============================================================

from .chart_renderer import chart_angle
from .theme import get_theme

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Node": "☊",
    "Lilith": "⚸",
    "Fortune": "⊗",
}


def draw_planets(ax, chart, r_planets=0.70, theme_name="dark", show_points=True):
    theme = get_theme(theme_name)
    planets = chart.get("planets", {})
    points = chart.get("points", {}) if show_points else {}

    # سیارات
    for name, data in planets.items():
        lon = data["lon"]
        theta = chart_angle(lon)
        symbol = PLANET_SYMBOLS.get(name, "•")

        ax.text(
            theta,
            r_planets,
            symbol,
            ha="center",
            va="center",
            fontsize=theme["planet_size"],
            color=theme["planet_color"],
            fontname=theme["font"],
            zorder=5,
        )

        deg = round(lon % 30, 1)
        ax.text(
            theta,
            r_planets + 0.06,
            f"{deg}°",
            ha="center",
            va="center",
            fontsize=theme["planet_label_size"],
            color=theme["planet_label_color"],
            fontname=theme["font"],
        )

    # نقاط حساس (Part of Fortune, Node, Lilith, ...)
    for name, data in points.items():
        lon = data["lon"]
        theta = chart_angle(lon)
        symbol = PLANET_SYMBOLS.get(name, "•")

        ax.text(
            theta,
            r_planets - 0.10,
            symbol,
            ha="center",
            va="center",
            fontsize=theme["planet_label_size"],
            color=theme["planet_label_color"],
            fontname=theme["font"],
            zorder=4,
        )
