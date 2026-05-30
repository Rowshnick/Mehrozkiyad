# ============================================================
#  PUBLIC API LAYER (LAYER 4)
#  AstroChart – Unified interface for the whole engine
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple, List
import json

from astrology_core.Engine.chart_engine import build_chart
from astrology_core.Core.transits import compute_transits_to_natal
from astrology_core.Core.progressions import compute_secondary_progressions
from astrology_core.Render.advanced_renderer import (
    render_chart_pretty,
    animate_transits as _animate_transits_impl,
)

ChartDict = Dict[str, Any]


@dataclass
class AstroChart:
    chart: ChartDict

    # --------------------------------------------------------
    #  Constructors
    # --------------------------------------------------------

    @classmethod
    def from_chart_dict(cls, chart: ChartDict) -> "AstroChart":
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

    @classmethod
    def from_json(cls, s: str) -> "AstroChart":
        """
        ساخت AstroChart از رشتهٔ JSON.
        """
        data = json.loads(s)
        return cls(chart=data)

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
    #  Fine-grained getters
    # --------------------------------------------------------

    def get_planet(self, name: str) -> Dict[str, Any] | None:
        """
        گرفتن اطلاعات یک سیاره، مثلاً get_planet("Mars")
        """
        return self.get_planets().get(name)

    def get_house(self, index: int) -> Dict[str, Any] | None:
        """
        گرفتن اطلاعات یک خانه، مثلاً get_house(7)
        """
        return self.get_houses().get(f"Cusp{index}")

    def get_point(self, name: str) -> Dict[str, Any] | None:
        """
        گرفتن اطلاعات یک نقطهٔ حساس، مثلاً get_point("Fortune")
        """
        return self.get_points().get(name)

    def get_aspects_of(self, body_name: str) -> List[Dict[str, Any]]:
        """
        همهٔ جنبه‌های مربوط به یک سیاره/نقطه، مثلاً "Sun"
        """
        aspects_block = self.get_aspects()
        aspects = aspects_block.get("planet_aspects", []) or aspects_block.get("aspects", [])
        result = []
        for a in aspects:
            p1 = a.get("planet1") or a.get("p1")
            p2 = a.get("planet2") or a.get("p2")
            if p1 == body_name or p2 == body_name:
                result.append(a)
        return result

    # --------------------------------------------------------
    #  Serialization
    # --------------------------------------------------------

    def to_json(self, indent: int | None = 2) -> str:
        """
        تبدیل چارت به JSON (برای ذخیره‌سازی/انتقال).
        """
        return json.dumps(self.chart, ensure_ascii=False, indent=indent)

    # --------------------------------------------------------
    #  Summary
    # --------------------------------------------------------

    def summary(self) -> str:
        """
        خلاصه‌ای متنی از چارت: سیارات، خانه‌ها، سیستم خانه، زمان و مکان.
        """
        meta = self.get_meta()
        planets = self.get_planets()
        houses = self.get_houses()

        lines: List[str] = []
        lines.append("AstroChart Summary")
        lines.append("------------------")
        lines.append(f"Datetime: {meta.get('datetime')}")
        lines.append(f"Lat/Lon:  {meta.get('lat')}, {meta.get('lon')}")
        lines.append(f"TZ:       {meta.get('tz_offset')}")
        lines.append(f"House system: {meta.get('house_system')}")
        lines.append("")
        lines.append("Planets:")
        for name, data in planets.items():
            lon = data.get("lon")
            lines.append(f"  - {name}: {lon:.2f}°")
        lines.append("")
        lines.append("Houses (cusps):")
        for i in range(1, 13):
            cusp = houses.get(f"Cusp{i}")
            if cusp:
                lines.append(f"  - House {i}: {cusp['lon']:.2f}°")
        return "\n".join(lines)

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
        meta = self.get_meta()
        natal_str = meta.get("datetime")
        tz_offset = meta.get("tz_offset", 0.0)
        lat = meta.get("lat")
        lon = meta.get("lon")

        if not natal_str or lat is None or lon is None:
            raise ValueError("Meta اطلاعات کافی برای ترانزیت ندارد (datetime/lat/lon).")

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

