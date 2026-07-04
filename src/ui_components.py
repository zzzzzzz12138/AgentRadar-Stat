from __future__ import annotations

import html
from typing import Any

import pandas as pd

from .theme import COLORS, FONT_FAMILY, HEADING_FONT_FAMILY, LEVEL_COLORS, RISK_COLORS, display_data_mode


ICE_BLUE_CSS = f"""
<style>
:root {{
  --primary:{COLORS['primary']}; --cyan:{COLORS['cyan']}; --blue:{COLORS['blue']};
  --bg:{COLORS['bg']}; --bg-soft:{COLORS['bg_soft']}; --card:{COLORS['card']};
  --text:{COLORS['text']}; --muted:{COLORS['muted']}; --line:{COLORS['line']};
  --success:{COLORS['success']}; --warning:{COLORS['warning']}; --danger:{COLORS['danger']};
}}
.stApp {{
  background:
    linear-gradient(rgba(248,252,255,.88), rgba(248,252,255,.93)),
    url("assets/agent_radar_bg.svg"),
    radial-gradient(circle at top left, rgba(56,189,248,.18), transparent 28%),
    linear-gradient(135deg, var(--bg) 0%, var(--bg-soft) 50%, #F0FBFF 100%);
  background-size: cover, cover, auto, auto;
  background-attachment: fixed;
  color: var(--text);
  font-family: {FONT_FAMILY};
}}
[class*="css"], .stMarkdown, .stText, .stDataFrame, button, input, textarea {{ font-family: {FONT_FAMILY}; }}
h1,h2,h3,h4,h5,h6 {{ font-family: {HEADING_FONT_FAMILY}; }}
[data-testid="stSidebar"] {{
  background: rgba(255,255,255,.88);
  border-right: 1px solid var(--line);
  box-shadow: 8px 0 28px rgba(96,165,250,.10);
}}
[data-testid="stSidebar"] * {{ letter-spacing: 0; }}
.block-container {{ padding-top: 1.4rem; max-width: 1420px; }}
.hero {{
  position: relative; padding: 30px 32px; border: 1px solid var(--line);
  border-radius: 24px; background: linear-gradient(120deg, #FFFFFF 0%, #EAF9FF 100%);
  box-shadow: 0 18px 44px rgba(56,189,248,.18); margin-bottom: 18px; overflow:hidden;
}}
.hero:after {{
  content:""; position:absolute; right:24px; top:18px; width:220px; height:120px;
  background: linear-gradient(135deg, rgba(56,189,248,.18), rgba(34,211,238,.08));
  border-radius: 999px; filter: blur(6px);
}}
.hero h1 {{ margin: 0 0 8px 0; font-size: 40px; color: #0F172A; line-height:1.05; }}
.hero p {{ max-width: 780px; margin: 0 0 14px 0; color: var(--muted); font-size: 16px; }}
.muted {{ color: var(--muted); }}
.metric-card {{
  background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 16px 18px;
  box-shadow: 0 10px 26px rgba(96,165,250,.12); min-height: 112px;
}}
.metric-card .label {{ color: var(--muted); font-size: 13px; }}
.metric-card .value {{ color: #0F172A; font-size: 25px; font-weight: 780; margin-top: 8px; line-height:1.15; }}
.flow-wrap {{ display:grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 12px; margin: 12px 0 4px; }}
.flow-card {{
  background: #FFFFFF; border: 1px solid var(--line); border-radius: 16px; padding: 14px 10px;
  text-align:center; box-shadow: 0 8px 20px rgba(34,211,238,.10); min-height: 86px;
}}
.flow-card b {{ display:block; color:#0F172A; font-size: 13px; }}
.flow-card span {{ color: var(--muted); font-size: 12px; }}
.badge {{ display:inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 760; color: white; margin: 2px 4px 2px 0; white-space:nowrap; }}
.badge-soft {{ display:inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 760; background: #E0F7FF; color: #0369A1; border: 1px solid #BAE6FD; margin: 2px 4px 2px 0; white-space:nowrap; }}
.section-card, .agent-card, .insight-card {{
  background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 18px;
  box-shadow: 0 10px 26px rgba(96,165,250,.10); margin: 12px 0;
}}
.agent-card {{ border-left: 5px solid var(--primary); }}
.critic-card {{ border-left: 5px solid var(--warning); }}
.project-card {{ border-left: 5px solid var(--success); }}
.data-table table {{ border-collapse: collapse; width: 100%; background: #fff; border-radius: 14px; overflow: hidden; }}
.data-table th {{ background: #EAF9FF; color: #0F172A; padding: 10px; font-size: 13px; border-bottom: 1px solid var(--line); }}
.data-table td {{ border-bottom: 1px solid #E2F3FB; padding: 9px; font-size: 13px; vertical-align: top; }}
.data-table tr:hover td {{ background:#F8FCFF; }}
.export-card {{
  background: linear-gradient(120deg,#FFFFFF,#EAF9FF); border: 1px solid var(--line);
  border-radius: 20px; padding: 18px; box-shadow: 0 12px 28px rgba(96,165,250,.13);
}}
.pdf-icon {{ font-size: 32px; line-height:1; display:inline-block; margin-right:8px; }}
@media print {{
  .stApp {{ background:#fff; }}
}}
div[data-testid="stTabs"] button {{ border-radius: 999px; }}
.stButton>button {{
  border-radius: 999px; border: 1px solid #BAE6FD; background: linear-gradient(120deg,#FFFFFF,#EAF9FF);
  color:#0369A1; font-weight: 740;
}}
.stDataFrame {{ border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
@media (max-width: 900px) {{ .flow-wrap {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} .hero h1 {{ font-size: 32px; }} }}
</style>
"""


def badge(label: Any, color: str = COLORS["primary"]) -> str:
    return f'<span class="badge" style="background:{color}">{html.escape(str(label))}</span>'


def soft_badge(label: Any) -> str:
    return f'<span class="badge-soft">{html.escape(str(label))}</span>'


def level_badge(level: Any) -> str:
    value = str(level)
    return badge(value, LEVEL_COLORS.get(value, COLORS["muted"]))


def risk_level(score: float) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def risk_badge(score: float) -> str:
    level = risk_level(float(score))
    label = {"low": "低风险", "medium": "中风险", "high": "高风险"}[level]
    return badge(label, RISK_COLORS[level])


def source_badge(source: Any) -> str:
    source = str(source)
    return badge(display_data_mode(source), COLORS["success"] if source == "api_live" else COLORS["warning"])


def metric_card_html(label: str, value: Any, note: str = "") -> str:
    return f'<div class="metric-card"><div class="label">{html.escape(label)}</div><div class="value">{html.escape(str(value))}</div><div class="muted">{html.escape(str(note))}</div></div>'


def flow_cards_html(items: list[tuple[str, str]]) -> str:
    cards = [f"<div class='flow-card'><b>{html.escape(title)}</b><span>{html.escape(desc)}</span></div>" for title, desc in items]
    return "<div class='flow-wrap'>" + "".join(cards) + "</div>"


def friendly_project_frame(df: pd.DataFrame, top_n: int = 20, sort_by: str = "final_potential_score", ascending: bool = False) -> pd.DataFrame:
    """Return a display-safe project table with friendly column names and no long text fields."""
    if df.empty:
        return pd.DataFrame()
    view = df.sort_values(sort_by, ascending=ascending).head(top_n).copy()
    rows: list[dict[str, Any]] = []
    for _, row in view.iterrows():
        url = row.get("repo_url") or row.get("html_url") or ""
        rows.append(
            {
                "仓库名称": str(row.get("full_name", "")),
                "链接": str(url),
                "项目主题": project_topic(row),
                "主要语言": str(row.get("language", "Unknown")),
                "Stars": int(row.get("stars_total", 0) or 0),
                "Forks": int(row.get("forks_total", 0) or 0),
                "推荐等级": str(row.get("recommendation_level", "")),
                "综合潜力分": round(float(row.get("final_potential_score", 0) or 0), 2),
                "个性化分": round(float(row.get("personalized_score", row.get("base_score", 0)) or 0), 2),
                "风险分": round(float(row.get("risk_score", 0) or 0), 2),
                "项目类型": str(row.get("cluster_name", "n/a")),
            }
        )
    return pd.DataFrame(rows)


def format_project_table(df: pd.DataFrame, top_n: int = 20, sort_by: str = "final_potential_score", ascending: bool = False) -> str:
    if df.empty:
        return "<p class='muted'>No rows available.</p>"
    view = df.sort_values(sort_by, ascending=ascending).head(top_n).copy()
    rows = []
    for _, row in view.iterrows():
        repo = html.escape(str(row.get("full_name", "")))
        url = html.escape(str(row.get("repo_url") or row.get("html_url") or ""))
        repo_html = f'<a href="{url}" target="_blank">{repo}</a>' if url else repo
        risk = float(row.get("risk_score", 0) or 0)
        rank = len(rows) + 1
        item = {
            "名次": rank,
            "仓库名称": repo_html,
            "项目主题": html.escape(project_topic(row)),
            "主要语言": html.escape(str(row.get("language", "Unknown"))),
            "Stars": int(row.get("stars_total", 0) or 0),
            "Forks": int(row.get("forks_total", 0) or 0),
            "推荐等级": level_badge(row.get("recommendation_level", "")),
            "综合潜力分": f"{float(row.get('final_potential_score', 0) or 0):.2f}",
            "风险分": f"{risk:.2f} {risk_badge(risk)}",
            "项目类型": soft_badge(row.get("cluster_name", "n/a")),
        }
        if sort_by == "risk_score":
            item["风险提示"] = "建议先检查维护活跃度、Issue 压力与复现成本"
        rows.append(item)
    return '<div class="data-table">' + pd.DataFrame(rows).to_html(index=False, escape=False) + "</div>"


def project_topic(row: Any) -> str:
    """Infer a short Chinese topic label from topics, description, and repository name."""
    text = " ".join(
        str(row.get(col, "") or "").lower()
        for col in ["full_name", "repo_name", "description", "topics", "readme_text", "cluster_name"]
        if hasattr(row, "get")
    )
    checks = [
        ("MCP工具生态", ["mcp", "model-context-protocol"]),
        ("编程智能体", ["coding", "code-agent", "developer", "computer-use", "codex"]),
        ("检索增强生成", ["rag", "retrieval", "vector", "embedding"]),
        ("工作流自动化", ["workflow", "automation", "orchestration"]),
        ("数据智能体", ["data-agent", "data analysis", "analytics"]),
        ("多智能体协作", ["multi-agent", "autogen", "crewai", "metagpt"]),
        ("本地大模型", ["local-llm", "ollama", "llama"]),
        ("智能体框架", ["agent", "assistant", "autonomous"]),
    ]
    for label, terms in checks:
        if any(term in text for term in terms):
            return label
    return "AI Agent 生态"
