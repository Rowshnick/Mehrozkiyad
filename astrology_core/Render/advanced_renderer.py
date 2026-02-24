# ============================================================
#  ADVANCED RENDERER (THEME-DRIVEN VERSION)
#  Fully rewritten for Roshina Project
# ============================================================

import math
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .theme import get_theme
from .chart_renderer import chart_angle


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
#  SAVE FUNCTION
# ============================================================

def save_chart(fig, filename="chart_output", directory="/content", format="png", dpi=300):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.{format}")
    fig.savefig(filepath, format=format, dpi=dpi)
    return filepath


# ============================================================
#  MAIN RENDERER (THEME-DRIVEN)
# ============================================================

def render_chart_pretty(
    chart,
    theme="dark",
    show_aspects=True,
    show_houses=True,
    show_points=True,
    dpi=200,
    figsize=(8, 8),
    save_as=None,
    save_dir="/content",
    save_name="chart",
):

    theme = get_theme(theme)

    fig, ax = plt.subplots(
        figsize=figsize,
        dpi=dpi,
        subplot_kw={"projection": "polar"}
    )

    # Theme background
    ax.set_facecolor(theme["background"])
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")
    ax.set_xticks([])
    ax.set_yticks([])

    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # -----------------------------
    #  Zodiac Circle
    # -----------------------------
    circle = plt.Circle(
        (0, 0),
        r_zodiac,
        transform=ax.transData._b,
        fill=False,
        color=theme["zodiac_circle"],
        linewidth=theme["zodiac_ring_width"],
    )
    ax.add_artist(circle)

    # Zodiac labels
    for i in range(12):
        lon = i * 30 + 15
        theta = chart_angle(lon)
        ax.text(
            theta,
            r_zodiac + 0.04,
            ZODIAC_SIGNS[i],
            ha="center",
            va="center",
            fontsize=theme["zodiac_size"],
            color=theme["zodiac_text"],
            fontname=theme["font"],
        )

    # -----------------------------
    #  Houses
    # -----------------------------
    houses = normalize_houses(chart.get("houses"))
    if show_houses and houses:
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
                zorder=1,
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

    # -----------------------------
    #  Planets
    # -----------------------------
    planets = chart.get("planets", {})
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

    # -----------------------------
    #  Sensitive Points
    # -----------------------------
    if show_points:
        points = chart.get("points", {})
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

    # -----------------------------
    #  Aspects
    # -----------------------------
    if show_aspects:
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
            lw = 0.6 + 2.0 * max(0.0, min(1.0, strength))

            ax.plot(
                [theta1, theta2],
                [r_planets, r_planets],
                color=color,
                linewidth=lw,
                alpha=theme["aspect_line_alpha"],
                zorder=3,
            )

    ax.set_rlim(0, 1.1)
    plt.tight_layout()

    if save_as:
        save_chart(fig, filename=save_name, directory=save_dir, format=save_as, dpi=dpi)

    return fig


# ============================================================
#  TRANSIT ANIMATION (THEME-DRIVEN)
# ============================================================

def animate_transits(
    natal_chart,
    transit_charts,
    theme="dark",
    dpi=150,
    figsize=(8, 8),
    interval=200,
):
    theme = get_theme(theme)

    fig = render_chart_pretty(natal_chart, theme=theme, show_aspects=False)
    ax = fig.axes[0]

    r_planets_transit = 0.55

    transit_texts = []
    transit_scat = ax.scatter([], [], color=theme["planet_color"], s=18, zorder=6)

    def init():
        transit_scat.set_offsets([])
        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()
        return [transit_scat]

    def update(frame_idx):
        chart_tr = transit_charts[frame_idx]
        planets_tr = chart_tr.get("planets", {})

        thetas = []
        rs = []
        for name, data in planets_tr.items():
            lon = data["lon"]
            theta = chart_angle(lon)
            thetas.append(theta)
            rs.append(r_planets_transit)

        xs = [r * math.cos(t) for r, t in zip(rs, thetas)]
        ys = [r * math.sin(t) for r, t in zip(rs, thetas)]
        offsets = list(zip(xs, ys))
        transit_scat.set_offsets(offsets)

        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()

        for (name, data), theta in zip(planets_tr.items(), thetas):
            symbol = PLANET_SYMBOLS.get(name, "•")
            txt = ax.text(
                theta,
                r_planets_transit + 0.05,
                symbol,
                ha="center",
                va="center",
                fontsize=theme["planet_label_size"],
                color=theme["planet_color"],
                zorder=7,
            )
            transit_texts.append(txt)

        return [transit_scat] + transit_texts

    anim = FuncAnimation(
        fig,
        update,
        frames=len(transit_charts),
        init_func=init,
        blit=False,
        interval=interval,
        repeat=True,
    )

    return fig, anim
