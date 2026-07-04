from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import plotly.graph_objects as go


FONT_FAMILY = '"Times New Roman", "SimSun", "宋体", serif'
TITLE_FONT_FAMILY = '"Times New Roman", "SimSun", "宋体", serif'
HEADING_FONT_FAMILY = '"Times New Roman", "SimSun", "宋体", serif'
NUMERIC_FONT_FAMILY = '"Times New Roman", "SimSun", "宋体", serif'
PLOTLY_FONT_FAMILY = "Times New Roman, SimSun, Microsoft YaHei, Arial"

COLORS: dict[str, str] = {
    "primary": "#38BDF8",
    "cyan": "#22D3EE",
    "blue": "#60A5FA",
    "bg": "#F8FCFF",
    "bg_soft": "#EEF8FF",
    "card": "#FFFFFF",
    "text": "#0F172A",
    "muted": "#64748B",
    "success": "#0EA5E9",
    "warning": "#FDBA74",
    "danger": "#DC2626",
    "purple": "#818CF8",
    "line": "#D8EEF8",
    "grid": "#E2F3FB",
}

PALETTE = ["#0EA5E9", "#38BDF8", "#7DD3FC", "#60A5FA", "#93C5FD", "#BAE6FD", "#CBD5E1", "#818CF8"]
LEVEL_COLORS = {"A": "#0EA5E9", "B": "#38BDF8", "C": "#93C5FD", "D": "#CBD5E1"}
RISK_COLORS = {"low": "#93C5FD", "medium": "#FDBA74", "high": "#DC2626"}


def plotly_layout(title: str | None = None, height: int | None = None) -> dict[str, Any]:
    """Return a shared ice-blue Plotly layout."""
    layout: dict[str, Any] = {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": COLORS["card"],
        "font": {"family": PLOTLY_FONT_FAMILY, "color": COLORS["text"], "size": 13},
        "title": {"text": "", "font": {"size": 18, "color": "#0F172A"}},
        "legend": {"orientation": "h", "y": -0.18, "title": {"font": {"size": 13}}},
        "hoverlabel": {
            "bgcolor": "rgba(248,252,255,0.96)",
            "bordercolor": "#38BDF8",
            "font": {"family": PLOTLY_FONT_FAMILY, "size": 13, "color": COLORS["text"]},
            "align": "left",
        },
        "margin": {"l": 52, "r": 28, "t": 24, "b": 52},
        "xaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["line"]},
        "yaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["line"]},
    }
    if height:
        layout["height"] = height
    return layout


def style_plotly(fig: go.Figure, title: str | None = None, height: int | None = None) -> go.Figure:
    """Apply the shared visual style to an existing Plotly figure."""
    fig.update_layout(**plotly_layout(title, height))
    return fig


def format_display_time(value: Any) -> str:
    """Format ISO/datetime values as reader-friendly UTC+8 display time."""
    if not value:
        return "未记录"
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return text.split(".")[0].replace("T", " ")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Pipeline timestamps are stored in UTC; display as China Standard Time.
    cst = dt.astimezone(timezone(timedelta(hours=8)))
    return f"{cst.year}年{cst.month}月{cst.day}日 {cst.hour:02d}:{cst.minute:02d} UTC+8"


def display_data_mode(mode: Any) -> str:
    """Return a presentation-friendly data source label."""
    return "GitHub 实时采集数据" if str(mode) == "api_live" else "离线兜底演示数据"
