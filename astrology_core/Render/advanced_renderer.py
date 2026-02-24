
# ============================================================
#  ADVANCED RENDERER (THEME-DRIVEN VERSION)
#  Fully rewritten by Roshina Project
# ============================================================

import math
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .theme import get_theme
from .chart_renderer import chart_angle
from .draw_zodiac import draw_zodiac_circle, draw_zodiac_labels
from .draw_houses import draw_houses
from .draw_planets import draw_planets
from .draw_aspects import draw_aspects

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


def save_chart(fig, filename="chart_output", directory="/content", format="png", dpi=300):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{filename}.{format}")
    fig.savefig(filepath, format=format, dpi=dpi)
    return filepath


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
    theme_dict = get_theme(theme)

    fig, ax = plt.subplots(
        figsize=figsize,
        dpi=dpi,
        subplot_kw={"projection": "polar"}
    )

    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")
    ax.set_facecolor(theme_dict["background"])
    ax.set_xticks([])
    ax.set_yticks([])

    r_zodiac = 0.85
    r_planets = 0.70
    r_houses = 0.95

    # زودیاک
    draw_zodiac_circle(ax, r_zodiac=r_zodiac, theme_name=theme)
    draw_zodiac_labels(ax, r_zodiac=r_zodiac, theme_name=theme)

    # خانه‌ها
    draw_houses(ax, chart, r_houses=r_houses, theme_name=theme, show_houses=show_houses)

    # سیارات و نقاط
    draw_planets(ax, chart, r_planets=r_planets, theme_name=theme, show_points=show_points)

    # جنبه‌ها
    draw_aspects(ax, chart, r_planets=r_planets, theme_name=theme, show_aspects=show_aspects)

    ax.set_rlim(0, 1.1)
    plt.tight_layout()

    if save_as:
        save_chart(fig, filename=save_name, directory=save_dir, format=save_as, dpi=dpi)

    return fig


def animate_transits(
    natal_chart,
    transit_charts,
    theme="dark",
    dpi=150,
    figsize=(8, 8),
    interval=200,
):
    theme_dict = get_theme(theme)

    fig = render_chart_pretty(natal_chart, theme=theme, show_aspects=False)
    ax = fig.axes[0]

    r_planets_transit = 0.55

    transit_texts = []
    transit_scat = ax.scatter([], [], color=theme_dict["planet_color"], s=18, zorder=6)

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
                fontsize=theme_dict["planet_label_size"],
                color=theme_dict["planet_color"],
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
