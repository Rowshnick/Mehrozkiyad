# advanced_renderer.py
# رندر پیشرفتهٔ چارت + انیمیشن ترانزیت

from __future__ import annotations

from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation

ChartDict = Dict[str, Any]


# ------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------

def _deg_to_rad(deg: float) -> float:
    return np.deg2rad(deg)


def _polar_to_cartesian(lon_deg: float, r: float = 1.0) -> Tuple[float, float]:
    """
    تبدیل طول دایرةالبروجی (درجه) به مختصات کارتزین روی دایره.
    0° = Aries = سمت راست (x مثبت)
    """
    angle = _deg_to_rad(90 - lon_deg)  # چرخش برای قرار دادن 0° در سمت راست
    x = r * np.cos(angle)
    y = r * np.sin(angle)
    return x, y


def _get_theme_colors(theme: str) -> Dict[str, str]:
    if theme == "light":
        return {
            "bg": "#ffffff",
            "fg": "#000000",
            "circle": "#444444",
            "planet": "#222222",
            "house": "#888888",
            "aspect_major": "#ff5555",
            "aspect_minor": "#ffaa00",
        }
    # default: dark
    return {
        "bg": "#111111",
        "fg": "#eeeeee",
        "circle": "#666666",
        "planet": "#ffffff",
        "house": "#aaaaaa",
        "aspect_major": "#ff6666",
        "aspect_minor": "#ffcc66",
    }


# ------------------------------------------------------------
#  Static chart rendering
# ------------------------------------------------------------

def render_chart_pretty(
    chart: ChartDict,
    theme: str = "dark",
    show_aspects: bool = True,
    show_houses: bool = True,
    show_points: bool = True,
    dpi: int = 200,
    figsize: Tuple[int, int] = (8, 8),
    save_as: Optional[str] = None,
    save_dir: str = ".",
    save_name: str = "chart",
):
    """
    رندر چارت ناتال (یا هر چارت دیگری) روی یک چرخ ساده و زیبا.
    """
    colors = _get_theme_colors(theme)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(colors["bg"])
    ax.set_facecolor(colors["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    # دایرهٔ اصلی
    outer = Circle((0, 0), 1.0, edgecolor=colors["circle"], facecolor="none", lw=2)
    inner = Circle((0, 0), 0.7, edgecolor=colors["circle"], facecolor="none", lw=1)
    ax.add_patch(outer)
    ax.add_patch(inner)

    planets = chart.get("planets", {})
    houses = chart.get("houses", {})
    points = chart.get("points", {})
    aspects_block = chart.get("aspects", {})
    planet_aspects = aspects_block.get("planet_aspects", []) or aspects_block.get("aspects", [])

    # سیارات
    for name, data in planets.items():
        lon = float(data.get("lon", 0.0))
        x, y = _polar_to_cartesian(lon, r=0.85)
        ax.scatter(x, y, color=colors["planet"], s=30, zorder=5)
        ax.text(
            x, y, name,
            color=colors["fg"],
            fontsize=8,
            ha="center",
            va="center",
            zorder=6,
        )

    # نقاط حساس
    if show_points:
        for name, data in points.items():
            lon = float(data.get("lon", 0.0))
            x, y = _polar_to_cartesian(lon, r=0.6)
            ax.scatter(x, y, color=colors["planet"], s=20, zorder=4)
            ax.text(
                x, y, name,
                color=colors["fg"],
                fontsize=7,
                ha="center",
                va="center",
                zorder=5,
            )

    # خانه‌ها
    if show_houses:
        for i in range(1, 13):
            cusp = houses.get(f"Cusp{i}")
            if not cusp:
                continue
            lon = float(cusp.get("lon", 0.0))
            x1, y1 = _polar_to_cartesian(lon, r=0.7)
            x2, y2 = _polar_to_cartesian(lon, r=1.0)
            ax.plot([x1, x2], [y1, y2], color=colors["house"], lw=0.8, zorder=1)
            xm, ym = _polar_to_cartesian(lon + 15, r=0.55)
            ax.text(
                xm, ym, str(i),
                color=colors["fg"],
                fontsize=8,
                ha="center",
                va="center",
                zorder=2,
            )

    # جنبه‌ها
    if show_aspects:
        for a in planet_aspects:
            p1 = a.get("planet1") or a.get("p1")
            p2 = a.get("planet2") or a.get("p2")
            if not p1 or not p2:
                continue

            body1 = planets.get(p1) or points.get(p1)
            body2 = planets.get(p2) or points.get(p2)
            if not body1 or not body2:
                continue

            lon1 = float(body1.get("lon", 0.0))
            lon2 = float(body2.get("lon", 0.0))
            x1, y1 = _polar_to_cartesian(lon1, r=0.9)
            x2, y2 = _polar_to_cartesian(lon2, r=0.9)

            atype = a.get("type", "major")
            if atype == "major":
                col = colors["aspect_major"]
                lw = 1.2
            else:
                col = colors["aspect_minor"]
                lw = 0.8

            ax.plot([x1, x2], [y1, y2], color=col, lw=lw, alpha=0.7, zorder=0)

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)

    if save_as is not None:
        import os
        path = os.path.join(save_dir, f"{save_name}.{save_as}")
        fig.savefig(path, dpi=dpi, facecolor=colors["bg"], bbox_inches="tight")
        plt.close(fig)
        return path

    return fig


# ------------------------------------------------------------
#  Transit animation
# ------------------------------------------------------------

def animate_transits(
    natal_chart: ChartDict,
    transit_charts: List[ChartDict],
    theme: str = "dark",
    dpi: int = 150,
    figsize: Tuple[int, int] = (8, 8),
    interval: int = 200,
):
    """
    انیمیشن سادهٔ ترانزیت روی چارت ناتال.
    """
    colors = _get_theme_colors(theme)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(colors["bg"])
    ax.set_facecolor(colors["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    # دایرهٔ اصلی
    outer = Circle((0, 0), 1.0, edgecolor=colors["circle"], facecolor="none", lw=2)
    inner = Circle((0, 0), 0.7, edgecolor=colors["circle"], facecolor="none", lw=1)
    ax.add_patch(outer)
    ax.add_patch(inner)

    natal_planets = natal_chart.get("planets", {})
    natal_points = natal_chart.get("points", {})
    natal_houses = natal_chart.get("houses", {})

    # ناتال ثابت
    for name, data in natal_planets.items():
        lon = float(data.get("lon", 0.0))
        x, y = _polar_to_cartesian(lon, r=0.85)
        ax.scatter(x, y, color=colors["planet"], s=30, zorder=5)
        ax.text(
            x, y, name,
            color=colors["fg"],
            fontsize=8,
            ha="center",
            va="center",
            zorder=6,
        )

    for name, data in natal_points.items():
        lon = float(data.get("lon", 0.0))
        x, y = _polar_to_cartesian(lon, r=0.6)
        ax.scatter(x, y, color=colors["planet"], s=20, zorder=4)
        ax.text(
            x, y, name,
            color=colors["fg"],
            fontsize=7,
            ha="center",
            va="center",
            zorder=5,
        )

    for i in range(1, 13):
        cusp = natal_houses.get(f"Cusp{i}")
        if not cusp:
            continue
        lon = float(cusp.get("lon", 0.0))
        x1, y1 = _polar_to_cartesian(lon, r=0.7)
        x2, y2 = _polar_to_cartesian(lon, r=1.0)
        ax.plot([x1, x2], [y1, y2], color=colors["house"], lw=0.8, zorder=1)

    # نقاط ترانزیت (scatter)
    transit_scat = ax.scatter([], [], color="#55aaff", s=25, zorder=7)
    transit_texts: List[Any] = []

    title_text = ax.text(
        0, 1.15, "",
        color=colors["fg"],
        fontsize=10,
        ha="center",
        va="center",
        transform=ax.transAxes,
    )

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)

    def init():
        # 🔴 اصلاح اصلی: آرایهٔ خالی ۲بعدی به‌جای []
        transit_scat.set_offsets(np.empty((0, 2)))
        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()
        title_text.set_text("")
        return [transit_scat, title_text]

    def update(frame_idx: int):
        if frame_idx >= len(transit_charts):
            return [transit_scat, title_text]

        chart = transit_charts[frame_idx]
        planets = chart.get("planets", {})
        meta = chart.get("meta", {})

        xs = []
        ys = []
        for name, data in planets.items():
            lon = float(data.get("lon", 0.0))
            x, y = _polar_to_cartesian(lon, r=0.95)
            xs.append(x)
            ys.append(y)

        # پاک کردن لیبل‌های قبلی
        for txt in transit_texts:
            txt.remove()
        transit_texts.clear()

        # لیبل‌های جدید
        for (name, data), x, y in zip(planets.items(), xs, ys):
            t = ax.text(
                x, y, name,
                color="#55aaff",
                fontsize=7,
                ha="center",
                va="center",
                zorder=8,
            )
            transit_texts.append(t)

        if xs and ys:
            coords = np.column_stack([xs, ys])
        else:
            # 🔴 اگر هیچ سیاره‌ای نباشد، باز هم آرایهٔ ۲بعدی خالی بده
            coords = np.empty((0, 2))

        transit_scat.set_offsets(coords)

        dt_str = meta.get("datetime", "")
        title_text.set_text(f"Transits – {dt_str}")

        return [transit_scat, title_text] + transit_texts

    anim = FuncAnimation(
        fig,
        update,
        frames=len(transit_charts),
        init_func=init,
        interval=interval,
        blit=False,
        repeat=True,
    )

    return fig, anim
