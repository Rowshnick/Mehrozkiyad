# ============================================================
#  CHART RENDERER (THEME-DRIVEN VERSION)
#  Fully rewritten for Roshina Project
# ============================================================

import math
import matplotlib.pyplot as plt

from .theme import get_theme


# ============================================================
#  CONSTANTS & SYMBOLS
# ============================================================

ZODIAC_SIGNS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓"
]

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

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


# ============================================================
#  ANGLE HELPERS
# ============================================================

def deg_to_rad(deg):
    return math.radians(deg)


def chart_angle(lon):
    """Convert ecliptic longitude to polar angle."""
    return deg_to_rad(90 - lon)


# ============================================================
#  NORMALIZATION HELPERS
# ============================================================

def normalize_houses(houses_raw):
    if isinstance(houses_raw, list):
        return {f"Cusp{i+1}": {"lon": houses_raw[i]} for i in range(len(houses_raw))}
    return houses_raw or {}


def normalize_aspects(aspects_raw):
    if isinstance(aspects_raw, list):
        return {"planet_aspects": aspects_raw}
    if isinstance(aspects_raw, dict):
        return aspects_raw
    return {"planet_aspects": []}


# ============================================================
#  BASIC RENDERER (THEME-DRIVEN)
# ============================================================

def render_chart(
    chart,
    theme="dark",
    show_aspects=True,
    show_houses=True,
    show_points=True,
    dpi=150,
    figsize=(8, 8),
):
    """
    Simple chart renderer (Theme-driven)
    Used for quick previews or lightweight rendering.
    """

    theme = get_theme(theme)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, subplot_kw={"projection": "polar"})
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")
    ax.set_facecolor(theme["background"])
    ax.set_xticks([])
    ax.set_yticks([])

    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # -------------------------
    #  Normalize data
    # -------------------------
    houses = normalize_houses(chart.get("houses"))
    aspects = normalize_aspects(chart.get("aspects"))
    planets = chart.get("planets", {})
    points = chart.get("points", {})

    # -------------------------
    #  Zodiac circle
    # -------------------------
    circle = plt.Circle(
        (0, 0),
        r_zodiac,
        transform=ax.transData._b,
        fill=False,
        color=theme["zodiac_circle"],
        linewidth=theme["zodiac_ring_width"],
    )
    ax.add_artist(circle)

    # Zodiac signs
    for i in range(12):
        lon = i * 30 + 15
        theta = chart_angle(lon)
        ax.text(
            theta,
            r_zodiac + 0.03,
            ZODIAC_SIGNS[i],
            ha="center",
            va="center",
            fontsize=theme["zodiac_size"],
            color=theme["zodiac_text"],
            fontname=theme["font"],
        )

    # -------------------------
    #  Houses
    # -------------------------
    if show_houses:
        for i in range(1, 13):
            cusp = houses.get(f"Cusp{i}")
            if not cusp:
                continue

            lon = cusp["lon"]
            theta = chart_angle(lon)

            ax.plot(
                [theta, theta],
                [0, r_houses],
                color=theme["house_lines"],
                linewidth=theme["house_line_width"],
            )

            ax.text(
                theta,
                r_houses + 0.02,
                str(i),
                ha="center",
                va="center",
                fontsize=theme["house_number_size"],
                color=theme["house_numbers"],
                fontname=theme["font"],
            )

    # -------------------------
    #  Planets
    # -------------------------
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

    # -------------------------
    #  Points
    # -------------------------
    if show_points:
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
            )

    # -------------------------
    #  Aspects
    # -------------------------
    if show_aspects:
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
            )

    ax.set_rlim(0, 1.1)
    plt.tight_layout()
    return fig
