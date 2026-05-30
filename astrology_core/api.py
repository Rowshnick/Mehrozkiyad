# ============================================================
#  PUBLIC API LAYER (LAYER 4)
#  AstroChart – Unified interface for the whole engine
#  Fully designed for Roshina Project
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

# --- Engine (real chart builder) ---
from astrology_core.Engine.chart_engine import build_chart

# --- Advanced engines (transits & progressions) ---
from astrology_core.Core.transits import compute_transits_to_natal
from astrology_core.Core.progressions import compute_secondary_progressions

# --- Render layer ---
from astrology_core.Render.advanced_renderer import (
    render_chart_pretty,
    animate_transits as _animate_transits_impl,
)


ChartDict = Dict[str, Any]


# ============================================================
#  AstroChart – main high-level object
# ============================================================

@dataclass
class AstroChart:
    chart: ChartDict

    # --------------------------------------------------------
    #  Constructors
    # --------------------------------------------------------

    @classmethod
    def from_chart_dict(cls, chart: ChartDict) -> "AstroChart":
        """
        ساخت AstroChart از یک دیکشنری آماده.
        این دیکشنری باید ساختار استاندارد زیر را داشته باشد:
        {
            "planets": {...},
            "houses": {...},
            "aspects": {...},
            "points": {...},
            "meta": {...}
        }
        """
        return cls(chart=chart)

    @classmethod
    def from_birth(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        lat: float,
        lon: float,
        tz_offset: float = 0.0,
        house_system: str = "placidus",
    ) -> "AstroChart":
        """
        ساخت چارت ناتال واقعی از داده‌های تولد.

        house_system:
            - "placidus"  (پیش‌فرض، استاندارد جهانی)
            - "whole_sign"
        """
        chart = build_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lat=lat,
            lon=lon,
            tz_offset=tz_offset,
            house_system=house_system,
        )
        return cls(chart=chart)

    # --------------------------------------------------------
    #  Basic accessors
    # --------------------------------------------------------

    def get_planets(self) -> Dict[str, Dict[str, Any]]:
        return self.chart.get("planets", {})

    def get_houses(self) -> Dict[str, Dict[str, Any]]:
        return self.chart.get("houses", {})

    def get_aspects(self) -> Dict[str, Any]:
        return self.chart.get("aspects", {})

    def get_points(self) -> Dict[str, Dict[str, Any]]:
        return self.chart.get("points", {})

    def get_meta(self) -> Dict[str, Any]:
        return self.chart.get("meta", {})

    # --------------------------------------------------------
    #  Rendering
    # --------------------------------------------------------

    def render(
        self,
        theme: str = "dark",
        show_aspects: bool = True,
        show_houses: bool = True,
        show_points: bool = True,
        dpi: int = 200,
        figsize: Tuple[int, int] = (8, 8),
    ):
        """
        رندر چارت با استفاده از رندرر پیشرفته.
        """
        fig = render_chart_pretty(
            self.chart,
            theme=theme,
            show_aspects=show_aspects,
            show_houses=show_houses,
            show_points=show_points,
            dpi=dpi,
            figsize=figsize,
        )
        return fig

    def save(
    self,
    theme: str = "dark",
    filename: str = "chart",
    directory: str = ".",
    fmt: str = "png",
    dpi: int = 300,
    show_aspects: bool = True,
    show_houses: bool = True,
    show_points: bool = True,
) -> str:
    """
    ذخیرهٔ چارت در قالب دلخواه (png, pdf, svg, ...)
    """
    fig = render_chart_pretty(
        self.chart,
        theme=theme,
        show_aspects=show_aspects,
        show_houses=show_houses,
        show_points=show_points,
        dpi=dpi,
        figsize=(8, 8),
        save_as=fmt,
        save_dir=directory,
        save_name=filename,
    )

    import os
    return os.path.join(directory, f"{filename}.{fmt}")
    
    # --------------------------------------------------------
    #  Animation (Transits)
    # --------------------------------------------------------

    def animate_transits(
        self,
        transit_charts: List[ChartDict],
        theme: str = "dark",
        dpi: int = 150,
        figsize: Tuple[int, int] = (8, 8),
        interval: int = 200,
    ):
        """
        ساخت انیمیشن ترانزیت‌ها روی چارت ناتال فعلی.
        transit_charts: لیستی از چارت‌های ترانزیتی (ساختار مشابه chart_engine).
        """
        fig, anim = _animate_transits_impl(
            natal_chart=self.chart,
            transit_charts=transit_charts,
            theme=theme,
            dpi=dpi,
            figsize=figsize,
            interval=interval,
        )
        return fig, anim

    # --------------------------------------------------------
    #  Advanced: Transits to this natal chart
    # --------------------------------------------------------

    def transits_to(
        self,
        transit_year: int,
        transit_month: int,
        transit_day: int,
        transit_hour: int,
        transit_minute: int,
        transit_tz: float,
    ) -> Dict[str, Any]:
        """
        محاسبهٔ ترانزیت‌ها نسبت به این چارت ناتال.

        از Core/transits.py استفاده می‌کند.
        """
        meta = self.get_meta()
        natal_str = meta.get("datetime")
        tz_offset = meta.get("tz_offset", 0.0)
        lat = meta.get("lat")
        lon = meta.get("lon")

        if not natal_str or lat is None or lon is None:
            raise ValueError("Meta اطلاعات کافی برای ترانزیت ندارد (datetime/lat/lon).")

        # انتظار فرمت ساده "YYYY-M-D H:M"
        date_part, time_part = natal_str.split()
        y, m, d = [int(x) for x in date_part.split("-")]
        hh, mm = [int(x) for x in time_part.split(":")]

        result = compute_transits_to_natal(
            natal_year=y,
            natal_month=m,
            natal_day=d,
            natal_hour=hh,
            natal_minute=mm,
            natal_tz=tz_offset,
            natal_lat=lat,
            natal_lon=lon,
            transit_year=transit_year,
            transit_month=transit_month,
            transit_day=transit_day,
            transit_hour=transit_hour,
            transit_minute=transit_minute,
            transit_tz=transit_tz,
        )

        return result

    # --------------------------------------------------------
    #  Advanced: Secondary Progressions
    # --------------------------------------------------------

    def secondary_progressions(
        self,
        age_years: float,
    ) -> Dict[str, Any]:
        """
        محاسبهٔ پروگرشن ثانویه برای این چارت ناتال.

        age_years: سن (سال) در زمان مورد نظر.
        """
        meta = self.get_meta()
        natal_str = meta.get("datetime")
        tz_offset = meta.get("tz_offset", 0.0)
        lat = meta.get("lat")
        lon = meta.get("lon")

        if not natal_str or lat is None or lon is None:
            raise ValueError("Meta اطلاعات کافی برای پروگرشن ندارد (datetime/lat/lon).")

        date_part, time_part = natal_str.split()
        y, m, d = [int(x) for x in date_part.split("-")]
        hh, mm = [int(x) for x in time_part.split(":")]

        result = compute_secondary_progressions(
            natal_year=y,
            natal_month=m,
            natal_day=d,
            natal_hour=hh,
            natal_minute=mm,
            natal_tz=tz_offset,
            natal_lat=lat,
            natal_lon=lon,
            age_years=age_years,
        )

        return result
