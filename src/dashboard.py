from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .agent_display import load_agent_records
from .interactive_visualization import build_interactive_charts, plotly_script_tag
from .theme import COLORS, FONT_FAMILY, display_data_mode, format_display_time
from .utils import project_path


def generate_dashboard(config: dict[str, Any]) -> str:
    """Generate a Chinese defense big-screen dashboard with interactive charts."""
    scored = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    clustered = _read_csv(config["paths"].get("clustered_repos", "data/processed/clustered_repos.csv"))
    personalized = _read_csv("outputs/reports/personalized_recommendations.csv")
    task_a = _read_csv("outputs/reports/model_metrics_task_a.csv")
    task_b = _read_csv("outputs/reports/model_metrics_task_b.csv")
    feature_importance = _read_csv("outputs/reports/feature_importance.csv")
    torch_history = _read_csv("outputs/reports/torch_training_history.csv")
    run_summary = _read_json("outputs/reports/run_summary.json")
    collection_log = _read_json(config["paths"].get("collection_log", "data/raw/api_collection_log.json"))
    agents = load_agent_records()
    charts = build_interactive_charts(
        scored,
        clustered=clustered,
        task_a=task_a,
        task_b=task_b,
        feature_importance=feature_importance,
        torch_history=torch_history,
        personalized=personalized,
        run_summary=run_summary,
        collection_log=collection_log,
    )

    data_mode = "api_live" if "source_type" in scored and (scored["source_type"] == "api_live").any() else "sample_fallback"
    updated_at = format_display_time(datetime.now(timezone.utc))
    best_model = _best_model(task_a)
    a_count = int((scored["recommendation_level"] == "A").sum()) if "recommendation_level" in scored else 0
    kpis = [
        ("仓库样本量", len(scored), "GitHub 公开仓库"),
        ("关键词", len(collection_log.get("requested_keywords", run_summary.get("requested_keywords", []))), "扩展搜索词"),
        ("去重前", run_summary.get("raw_items_before_dedup", collection_log.get("raw_items_before_dedup", "n/a")), "候选项目"),
        ("去重后", run_summary.get("repos_after_dedup", collection_log.get("repos_after_dedup", "n/a")), "唯一仓库"),
        ("入模项目", run_summary.get("repo_count", len(scored)), "相关性过滤后"),
        ("A 级推荐", a_count, "优先展示"),
        ("最佳模型 F1", f"{best_model.get('f1', 0):.2f}", best_model.get("model_name", "n/a")),
        ("聚类类型 k", run_summary.get("best_k", "n/a"), run_summary.get("best_cluster_model", "n/a")),
        ("个性化推荐", len(personalized), "画像输出"),
        ("Agent 数", len(agents), "解释卡片"),
    ]

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentRadar-Stat 答辩大屏</title>
  {_style()}
  {plotly_script_tag()}
</head>
<body>
  <header class="hero">
    <div>
      <p class="eyebrow">课堂答辩投屏 · GitHub 开源生态智能雷达</p>
      <h1>AgentRadar-Stat 智能开源项目雷达</h1>
      <p>500 个 GitHub 公开仓库 · 多模型评分 · 个性化推荐 · DeepSeek Agent 解释</p>
      <div class="badges">
        <span>数据状态：{display_data_mode(data_mode) if data_mode != 'api_live' else 'GitHub 公开仓库数据'}</span>
        <span>报告状态：已生成</span>
        <span>Agent 状态：DeepSeek 解释已生成</span>
      </div>
    </div>
    <div class="time-card"><span>最近更新</span><b>{updated_at}</b></div>
  </header>

  <section class="kpi-row">
    {''.join(_kpi(label, value, note) for label, value, note in kpis)}
  </section>

  <section class="main-grid">
    <div class="panel large">{_panel_title("风险-潜力四象限", "现场讲解最直观：高潜力低风险优先推荐，高潜力高风险谨慎探索。")}{charts["risk_potential_quadrant"]}</div>
    <div class="panel large">{_panel_title("PCA 聚类项目地图", "展示 500 个项目在低维空间中的项目类型分布。")}{charts["pca_cluster_map"]}</div>
    <div class="panel">{_panel_title("综合潜力 Top 15", "快速展示最值得关注的项目。")}{_trim_chart(charts["top_potential"], 500)}</div>
    <div class="panel">{_panel_title("个性化推荐 Top 15", "同一批项目在用户画像下的排序。")}{charts["top_personalized"]}</div>
    <div class="panel compact">{_panel_title("数据采集漏斗", "采集、去重、过滤、README 与 Agent 规模。")}{charts["collection_funnel"]}</div>
    <div class="panel compact">{_panel_title("推荐等级占比", "A/B/C/D 项目结构。")}{charts["recommendation_donut"]}</div>
    <div class="panel compact">{_panel_title("聚类类型分布", "横向中文标签避免断裂。")}{charts["cluster_type_counts"]}</div>
    <div class="panel compact">{_panel_title("模型对比", "Task A / Task B 的 F1 与 AUC。")}{charts["model_comparison"]}</div>
  </section>
</body>
</html>"""
    out = project_path("outputs/dashboards/agent_radar_dashboard.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


def _style() -> str:
    return f"""<style>
:root{{--primary:{COLORS['primary']};--cyan:{COLORS['cyan']};--blue:{COLORS['blue']};--purple:{COLORS['purple']};--bg:{COLORS['bg']};--text:{COLORS['text']};--muted:{COLORS['muted']};--line:{COLORS['line']};}}
*{{box-sizing:border-box}} body{{margin:0;font-family:{FONT_FAMILY};color:var(--text);background:linear-gradient(rgba(248,252,255,.84),rgba(248,252,255,.92)),url("../../assets/agent_radar_bg.svg"),linear-gradient(135deg,#F8FCFF,#EEF8FF);background-size:cover,cover,auto;background-attachment:fixed;}}
.hero{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin:22px;padding:30px 34px;border:1px solid #BAE6FD;border-radius:28px;background:linear-gradient(120deg,rgba(255,255,255,.95),rgba(232,248,255,.90));box-shadow:0 22px 52px rgba(56,189,248,.18)}}
.eyebrow{{font-weight:850;color:#0369A1;margin:0 0 8px}} h1{{font-size:44px;line-height:1.05;margin:0 0 10px;color:#0F172A}} p{{color:#475569;line-height:1.6}} .badges span{{display:inline-block;margin:5px 8px 0 0;padding:6px 12px;border-radius:999px;background:#E0F7FF;border:1px solid #BAE6FD;color:#0369A1;font-weight:800;font-size:13px}}
.time-card{{min-width:260px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 12px 30px rgba(96,165,250,.12)}}.time-card span{{display:block;color:var(--muted);font-size:13px}}.time-card b{{display:block;color:#0F172A;font-size:20px;margin-top:6px}}
.kpi-row{{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:12px;padding:0 22px 18px}}.kpi{{background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:18px;padding:14px;box-shadow:0 10px 24px rgba(96,165,250,.10);min-height:104px}}.kpi .label{{font-size:12px;color:var(--muted)}}.kpi .value{{font-size:23px;font-weight:850;color:#0F172A;margin:8px 0 4px;word-break:break-word}}.kpi .note{{font-size:12px;color:var(--muted)}}
.main-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;padding:0 22px 28px}}.panel{{background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:22px;padding:14px;box-shadow:0 12px 30px rgba(96,165,250,.12);overflow:hidden}}.large{{grid-column:span 2}}.compact{{min-height:390px}}.panel h2{{font-size:18px;margin:0;color:#0F172A}}.panel .desc{{color:var(--muted);font-size:13px;line-height:1.5;margin:5px 0 8px}}
@media(max-width:1200px){{.kpi-row{{grid-template-columns:repeat(5,minmax(0,1fr))}}.main-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.large{{grid-column:span 2}}}}
@media(max-width:760px){{.hero{{display:block}}.kpi-row,.main-grid{{grid-template-columns:1fr}}.large{{grid-column:auto}}h1{{font-size:32px}}}}
@media print{{body{{background:#fff}}.panel,.kpi,.hero{{break-inside:avoid;page-break-inside:avoid;box-shadow:none}}}}
</style>"""


def _kpi(label: str, value: Any, note: str) -> str:
    return f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div><div class='note'>{note}</div></div>"


def _panel_title(title: str, desc: str) -> str:
    return f"<h2>{title}</h2><p class='desc'>{desc}</p>"


def _trim_chart(chart: str, _height: int) -> str:
    return chart


def _best_model(metrics: pd.DataFrame) -> dict[str, Any]:
    if metrics.empty or "f1" not in metrics.columns:
        return {}
    return metrics.sort_values("f1", ascending=False).iloc[0].to_dict()


def _read_csv(path: str) -> pd.DataFrame:
    target = project_path(path)
    return pd.read_csv(target) if target.exists() else pd.DataFrame()


def _read_json(path: str) -> dict[str, Any]:
    target = project_path(path)
    if not target.exists():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
