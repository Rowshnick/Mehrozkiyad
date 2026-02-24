#============================================================
#DRAW_HOUSES (THEME-DRIVEN VERSION)
#Fully rewritten by Roshina Project
#============================================================

from .angle_utils import chart_angle
from .theme import get_theme


def normalize_houses(houses_raw):
    if isinstance(houses_raw, list):
        return {f"Cusp{i+1}": {"lon": houses_raw[i]} for i in range(len(houses_raw))}
    return houses_raw or {}


def draw_houses(ax, chart, r_houses=0.95, theme_name="dark", show_houses=True):
    if not show_houses:
        return

    theme = get_theme(theme_name)
    houses = normalize_houses(chart.get("houses"))

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
