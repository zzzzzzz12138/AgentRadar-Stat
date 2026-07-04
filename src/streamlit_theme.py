from __future__ import annotations

from pathlib import Path
from typing import Any

import plotly.graph_objects as go

from .theme import COLORS, PALETTE, PLOTLY_FONT_FAMILY
from .utils import PROJECT_ROOT


STREAMLIT_FONT_STACK = '"Times New Roman", "SimSun", "宋体", serif'


def _background_data_uri() -> str:
    path = PROJECT_ROOT / "assets" / "agent_radar_bg.svg"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    from urllib.parse import quote

    return f"data:image/svg+xml;charset=utf-8,{quote(text)}"


def streamlit_css() -> str:
    """Return the showcase-level Streamlit CSS shared by all pages."""
    bg = _background_data_uri()
    bg_layer = f'url("{bg}"),' if bg else ""
    return f"""
<style>
:root {{
  --ar-primary:#38BDF8;
  --ar-ice:#7DD3FC;
  --ar-cyan:#22D3EE;
  --ar-blue:#60A5FA;
  --ar-fog:#93C5FD;
  --ar-bg:#F8FCFF;
  --ar-bg-soft:#EEF8FF;
  --ar-card:rgba(255,255,255,0.94);
  --ar-text:#0F172A;
  --ar-muted:#334155;
  --ar-soft:#64748B;
  --ar-line:#C7EFFF;
  --ar-grid:#E2F3FB;
  --ar-warning:#FB923C;
}}
.stApp {{
  background:
    linear-gradient(rgba(248,252,255,.90), rgba(248,252,255,.95)),
    {bg_layer}
    radial-gradient(circle at 8% 4%, rgba(56,189,248,.22), transparent 28%),
    linear-gradient(135deg, #F8FCFF 0%, #EEF8FF 55%, #F0FBFF 100%);
  background-size: cover, cover, auto, auto;
  background-attachment: fixed;
  color: var(--ar-text);
  font-family: {STREAMLIT_FONT_STACK};
}}
html, body, [class*="css"], .stMarkdown, .stText, .stDataFrame, .stSelectbox,
.stMultiSelect, .stSlider, button, input, textarea, label {{
  font-family: {STREAMLIT_FONT_STACK} !important;
  letter-spacing: 0 !important;
}}
h1,h2,h3,h4,h5,h6 {{
  font-family: {STREAMLIT_FONT_STACK} !important;
  color: var(--ar-text);
  letter-spacing: 0 !important;
}}
.block-container {{
  padding-top: 1.35rem;
  padding-bottom: 2.5rem;
  max-width: 1440px;
}}
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{
  display:none !important;
  visibility:hidden !important;
  height:0 !important;
}}
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, rgba(255,255,255,.96), rgba(238,248,255,.95));
  border-right: 1px solid var(--ar-line);
  box-shadow: 8px 0 28px rgba(96,165,250,.10);
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{
  color: var(--ar-muted);
}}
[data-baseweb="tag"] {{
  background: #E0F7FF !important;
  color: #075985 !important;
  border: 1px solid #BAE6FD !important;
  border-radius: 999px !important;
}}
[data-baseweb="tag"] svg {{ fill: #0284C7 !important; }}
.stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"] button {{
  border-radius: 999px !important;
  border: 1px solid #BAE6FD !important;
  background: linear-gradient(120deg,#FFFFFF,#EAF9FF) !important;
  color:#0369A1 !important;
  font-weight: 760 !important;
  box-shadow: 0 8px 20px rgba(56,189,248,.12);
}}
.stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"] button:hover {{
  border-color: #38BDF8 !important;
  box-shadow: 0 12px 26px rgba(56,189,248,.20);
}}
div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label, div[data-testid="stSlider"] label {{
  color: #0F172A !important;
  font-weight: 700 !important;
}}
div[data-testid="stRadio"] [role="radiogroup"] {{
  gap: 4px;
}}
input[type="radio"] {{
  accent-color: #38BDF8 !important;
}}
div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{
  border-color: #BAE6FD !important;
}}
[data-testid="stSidebar"] [role="radio"] > div:first-child {{
  border-color:#BAE6FD !important;
}}
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] > div:first-child {{
  border-color:#38BDF8 !important;
  background:#38BDF8 !important;
  box-shadow:0 0 0 3px rgba(56,189,248,.14) !important;
}}
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] > div:first-child > div {{
  background:#38BDF8 !important;
}}
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {{
  border-color:#BAE6FD !important;
}}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child {{
  background:#38BDF8 !important;
  border-color:#38BDF8 !important;
  box-shadow:0 0 0 3px rgba(56,189,248,.16) !important;
}}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child > div {{
  background:#38BDF8 !important;
}}
.stTabs [data-baseweb="tab-list"] {{
  gap: 8px;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: 999px;
  border: 1px solid #BAE6FD;
  background: #F0FBFF;
  padding: 8px 16px;
}}
.ar-hero {{
  position: relative;
  overflow: hidden;
  padding: 34px 36px 30px;
  border: 1px solid var(--ar-line);
  border-radius: 24px;
  background: linear-gradient(125deg, rgba(255,255,255,.98), rgba(232,248,255,.96));
  box-shadow: 0 22px 56px rgba(56,189,248,.18);
  margin-bottom: 18px;
}}
.ar-hero::after {{
  content:"";
  position:absolute;
  right:24px;
  top:18px;
  width:260px;
  height:140px;
  border-radius:999px;
  background: linear-gradient(135deg, rgba(56,189,248,.20), rgba(34,211,238,.08));
  filter: blur(8px);
}}
.ar-hero h1 {{
  position:relative;
  margin:0 0 8px 0;
  font-size: clamp(38px, 5vw, 64px);
  line-height: 1;
}}
.ar-hero .subtitle {{
  position:relative;
  font-size: 22px;
  color:#075985;
  font-weight: 800;
  margin-bottom: 10px;
}}
.ar-hero p {{
  position:relative;
  max-width: 980px;
  color: var(--ar-muted);
  font-size: 16px;
  line-height: 1.85;
}}
.tag-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; position:relative; }}
.ar-badge {{
  display:inline-flex;
  align-items:center;
  gap:5px;
  padding:5px 11px;
  border-radius:999px;
  border:1px solid #BAE6FD;
  background:#E0F7FF;
  color:#075985;
  font-size:12.5px;
  font-weight:760;
  white-space:nowrap;
}}
.ar-page-title {{
  margin: 8px 0 16px;
  padding: 20px 24px;
  border-left: 7px solid var(--ar-primary);
  border-radius: 18px;
  background: linear-gradient(90deg, rgba(232,248,255,.95), rgba(255,255,255,.88));
  box-shadow: 0 12px 28px rgba(96,165,250,.10);
}}
.ar-page-title h2 {{ margin:0 0 6px 0; font-size: 30px; }}
.ar-page-title p {{ margin:0; color: var(--ar-muted); line-height:1.8; }}
.metric-card, .ar-card, .project-card, .agent-showcase-card, .profile-card,
.chart-card, .text-card, .export-card {{
  background: var(--ar-card);
  border: 1px solid var(--ar-line);
  border-radius: 18px;
  box-shadow: 0 12px 28px rgba(96,165,250,.11);
  padding: 17px 18px;
  margin: 10px 0;
}}
.metric-card {{
  min-height: 118px;
}}
.metric-card .label {{
  color: var(--ar-muted);
  font-size: 13px;
  font-weight: 700;
}}
.metric-card .value {{
  color:#0F172A;
  font-size: 28px;
  font-weight: 820;
  line-height: 1.12;
  margin-top: 8px;
  overflow-wrap: anywhere;
}}
.metric-card .subvalue {{
  color:#0284C7;
  font-size: 14px;
  font-weight: 760;
  margin-top: 5px;
  display:block;
}}
.metric-card .note {{
  color:#64748B;
  font-size: 13px;
  margin-top: 5px;
}}
.ar-card h3, .ar-card h4, .project-card h4, .agent-showcase-card h4,
.chart-card h4, .text-card h4, .export-card h4 {{
  margin-top:0;
}}
.ar-card h3::after, .ar-card h4::after, .project-card h4::after,
.agent-showcase-card h4::after, .chart-card h4::after, .text-card h4::after {{
  content:"";
  display:block;
  width:58px;
  height:4px;
  margin-top:9px;
  border-radius:999px;
  background: linear-gradient(90deg,#38BDF8,#7DD3FC);
}}
.capability-flow {{
  display:grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin: 14px 0 18px;
}}
.capability-stage {{
  min-height: 174px;
  border: 1px solid var(--ar-line);
  border-radius: 18px;
  padding: 16px;
  background: linear-gradient(145deg,#FFFFFF,#EAF9FF);
  box-shadow: 0 10px 24px rgba(56,189,248,.12);
  position:relative;
}}
.capability-stage:not(:last-child)::after {{
  content:"→";
  position:absolute;
  right:-15px;
  top:50%;
  transform: translateY(-50%);
  color:#0284C7;
  font-size:24px;
  font-weight:800;
  z-index:2;
}}
.capability-stage b {{
  display:block;
  color:#0F172A;
  font-size:17px;
  margin-bottom:10px;
}}
.capability-node {{
  display:block;
  margin: 7px 0;
  padding: 6px 9px;
  border-radius:999px;
  background:#F0FBFF;
  border:1px solid #BAE6FD;
  color:#075985;
  font-size:12.5px;
  font-weight:740;
}}
.project-grid {{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 13px;
  margin: 10px 0 16px;
}}
.project-card {{
  min-height: 210px;
}}
.project-card h4 {{
  margin-bottom: 8px;
  font-size: 18px;
  overflow-wrap: anywhere;
}}
.project-card .topic {{
  min-height: 44px;
  color:#334155;
  line-height:1.65;
}}
.project-meta {{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}}
.project-meta span {{
  border:1px solid #D8EEF8;
  border-radius:12px;
  background:#F8FCFF;
  padding:6px 8px;
  color:#334155;
  font-size:13px;
}}
.readme-signal-grid {{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:12px;
  margin:12px 0 18px;
}}
.readme-signal {{
  min-width:0;
  border:1px solid #D8EEF8;
  border-radius:14px;
  background:linear-gradient(145deg,#FFFFFF,#F0FAFF);
  padding:13px 14px;
  box-shadow:0 8px 20px rgba(56,189,248,.08);
}}
.readme-signal b {{ display:block; color:#075985; font-size:14px; margin-bottom:5px; }}
.readme-signal span {{ color:#475569; font-size:12.5px; line-height:1.65; word-break:normal; overflow-wrap:break-word; }}
.wide-table {{
  width:100%;
  overflow-x:auto;
  border:1px solid var(--ar-line);
  border-radius:16px;
  background:#fff;
  box-shadow:0 10px 24px rgba(96,165,250,.08);
}}
.wide-table table {{
  width:100%;
  min-width: 980px;
  border-collapse:collapse;
}}
.wide-table th {{
  background:#EAF9FF;
  color:#0F172A;
  padding:11px 12px;
  border-bottom:1px solid var(--ar-line);
  text-align:center;
  white-space:nowrap;
}}
.wide-table td {{
  padding:10px 12px;
  border-bottom:1px solid #E2F3FB;
  color:#334155;
  text-align:center;
  vertical-align:middle;
  word-break: normal;
  overflow-wrap: break-word;
  line-height:1.55;
}}
.wide-table tr:hover td {{ background:#F8FCFF; }}
.progress-label {{
  display:flex;
  justify-content:space-between;
  color:#0F172A;
  font-weight:760;
  margin: 10px 0 4px;
}}
.custom-progress {{
  height:11px;
  border-radius:999px;
  background:#E2F3FB;
  overflow:hidden;
}}
.custom-progress span {{
  display:block;
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#38BDF8,#7DD3FC);
}}
.custom-progress.warning span {{
  background:linear-gradient(90deg,#FDBA74,#FB923C);
}}
.agent-section-grid {{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 10px;
}}
.agent-section {{
  border:1px solid #D8EEF8;
  border-radius:14px;
  background:#F8FCFF;
  padding:12px;
}}
.code-box {{
  white-space:pre-wrap;
  word-break:break-word;
  background:#0F172A;
  color:#E0F7FF;
  border-radius:14px;
  padding:14px;
  line-height:1.7;
  border:1px solid #38BDF8;
}}
a {{ color:#0369A1; text-decoration:none; font-weight:760; }}
a:hover {{ text-decoration:underline; }}
@media (max-width: 1100px) {{
  .capability-flow {{ grid-template-columns: 1fr; }}
  .capability-stage:not(:last-child)::after {{ display:none; }}
  .readme-signal-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
}}
@media (max-width: 680px) {{ .readme-signal-grid {{ grid-template-columns:1fr; }} }}
</style>
"""


def apply_streamlit_plotly_theme(
    fig: go.Figure,
    *,
    height: int | None = 440,
    legend_title: str | None = None,
) -> go.Figure:
    """Apply the Streamlit report-matched Plotly theme."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.96)",
        height=height,
        margin={"l": 58, "r": 28, "t": 38, "b": 58},
        font={"family": PLOTLY_FONT_FAMILY, "color": COLORS["text"], "size": 13},
        hoverlabel={
            "bgcolor": "rgba(248,252,255,0.98)",
            "bordercolor": "#38BDF8",
            "font": {"family": PLOTLY_FONT_FAMILY, "size": 13, "color": COLORS["text"]},
            "align": "left",
        },
        legend={
            "orientation": "h",
            "y": -0.18,
            "x": 0,
            "title": {"text": legend_title or "", "font": {"size": 13}},
        },
        xaxis={"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["line"], "title_font": {"size": 14}},
        yaxis={"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["line"], "title_font": {"size": 14}},
    )
    return fig


def blue_sequence() -> list[str]:
    """Return the restrained ice-blue sequence for Streamlit charts."""
    return ["#0EA5E9", "#38BDF8", "#7DD3FC", "#60A5FA", "#93C5FD", "#BAE6FD", "#CBD5E1"]


def chart_palette(index: int) -> str:
    return PALETTE[index % len(PALETTE)]


def format_hover_template(fields: list[tuple[str, str]]) -> str:
    """Build a Chinese Plotly hover template from display labels and customdata slots."""
    lines = [f"<b>%{{hovertext}}</b>"]
    for idx, (label, fmt) in enumerate(fields):
        suffix = fmt or ""
        lines.append(f"{label}：%{{customdata[{idx}]{suffix}}}")
    return "<br>".join(lines) + "<extra></extra>"


def rename_plotly_fields(mapping: dict[str, str], field: str) -> str:
    """Return a display label for a raw plotting field."""
    return mapping.get(field, field)


def relative_report_path(path: str | Path) -> str:
    try:
        return str(Path(path).relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return Path(path).name
