from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from src.agent_display import load_agent_records, load_single_project_cache
from src.personalization import compute_personalized_score, explain_personalized_match
from src.streamlit_components import (
    SCORE_LABELS,
    badge,
    capability_flow,
    chart_card,
    clean_sentence,
    display_cluster,
    display_feature,
    display_hardware,
    display_level,
    display_model,
    metric_card,
    page_header,
    progress_bar,
    project_topic,
    project_url,
    render_agent_showcase,
    render_metric_grid,
    render_profile_summary,
    render_project_cards,
    render_project_table,
    safe_text,
    text_card,
)
from src.streamlit_theme import apply_streamlit_plotly_theme, blue_sequence, format_hover_template, relative_report_path, streamlit_css
from src.user_profile import (
    GOAL_OPTIONS,
    HARDWARE_OPTIONS,
    LANGUAGE_OPTIONS,
    LEVEL_OPTIONS,
    OUTPUT_OPTIONS,
    RISK_OPTIONS,
    ROLE_OPTIONS,
    TOPIC_OPTIONS,
    build_user_profile_from_dict,
)
from src.utils import PROJECT_ROOT, project_path


st.set_page_config(page_title="AgentRadar-Stat", layout="wide", page_icon="📊", initial_sidebar_state="expanded")
st.markdown(streamlit_css(), unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def read_csv(path: str) -> pd.DataFrame:
    target = project_path(path)
    return pd.read_csv(target) if target.exists() else pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_json(path: str) -> dict[str, Any]:
    target = project_path(path)
    if not target.exists():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


@st.cache_data(show_spinner=False)
def read_config_without_env() -> dict[str, Any]:
    """Load config.yaml for paths only; Streamlit does not inspect local secret files."""
    path = PROJECT_ROOT / "config.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def file_exists(path: str) -> bool:
    return project_path(path).exists()


def pct(value: Any) -> float:
    return float(value or 0)


def repo_short(full_name: Any) -> str:
    text = safe_text(full_name)
    return text.split("/")[-1] if "/" in text else text


def html_escape(value: Any) -> str:
    import html

    return html.escape(safe_text(value))


def log_bins(series: pd.Series) -> pd.DataFrame:
    values = pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)
    bins = [0, 10, 50, 100, 500, 1000, 5000, 10000, float("inf")]
    labels = ["0-10", "10-50", "50-100", "100-500", "500-1k", "1k-5k", "5k-10k", "10k+"]
    out = pd.cut(values, bins=bins, labels=labels, include_lowest=True, right=False).value_counts(sort=False).reset_index()
    out.columns = ["Stars 区间", "项目数量"]
    return out


def topic_counts(frame: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    labels = frame.apply(project_topic, axis=1)
    return labels.value_counts().head(top_n).rename_axis("技术主题").reset_index(name="项目数量")


def plot_language_distribution(frame: pd.DataFrame, top_n: int) -> go.Figure:
    data = frame["language"].fillna("Unknown").value_counts().head(top_n).reset_index()
    data.columns = ["主要语言", "项目数量"]
    fig = go.Figure(
        go.Bar(
            x=data["主要语言"],
            y=data["项目数量"],
            marker={"color": np.linspace(0, 1, len(data)), "colorscale": [[0, "#BAE6FD"], [1, "#0EA5E9"]]},
            hovertemplate="主要语言：%{x}<br>项目数量：%{y}<extra></extra>",
        )
    )
    fig.update_xaxes(title="主要语言")
    fig.update_yaxes(title="项目数量")
    return apply_streamlit_plotly_theme(fig, height=420)


def plot_stars_distribution(frame: pd.DataFrame) -> go.Figure:
    data = log_bins(frame["stars_total"])
    fig = go.Figure(
        go.Bar(
            x=data["Stars 区间"],
            y=data["项目数量"],
            marker_color="#38BDF8",
            hovertemplate="Stars 区间：%{x}<br>项目数量：%{y}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Stars 对数分箱")
    fig.update_yaxes(title="项目数量")
    return apply_streamlit_plotly_theme(fig, height=400)


def plot_stars_forks(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    level_order = ["A", "B", "C", "D"]
    colors = {"A": "#0EA5E9", "B": "#38BDF8", "C": "#93C5FD", "D": "#CBD5E1"}
    for level in level_order:
        sub = frame[frame["recommendation_level"] == level].copy()
        if sub.empty:
            continue
        custom = np.column_stack(
            [
                sub["full_name"],
                sub["language"].fillna("Unknown"),
                sub["stars_total"].fillna(0).round(0),
                sub["forks_total"].fillna(0).round(0),
                sub["final_potential_score"].fillna(0).round(2),
                sub["repo_url"].fillna(""),
            ]
        )
        fig.add_trace(
            go.Scatter(
                x=sub["stars_total"].clip(lower=1),
                y=sub["forks_total"].clip(lower=1),
                mode="markers",
                name=display_level(level),
                hovertext=sub["full_name"],
                customdata=custom,
                marker={
                    "size": np.clip(np.log1p(sub["final_potential_score"]) * 5, 8, 18),
                    "color": colors[level],
                    "opacity": 0.72,
                    "line": {"color": "#FFFFFF", "width": 0.8},
                },
                hovertemplate=format_hover_template(
                    [
                        ("仓库", ""),
                        ("语言", ""),
                        ("Stars", ":,.0f"),
                        ("Forks", ":,.0f"),
                        ("综合潜力分", ":.2f"),
                        ("GitHub", ""),
                    ]
                ),
            )
        )
    fig.update_xaxes(title="Stars（对数刻度）", type="log")
    fig.update_yaxes(title="Forks（对数刻度）", type="log")
    return apply_streamlit_plotly_theme(fig, height=520, legend_title="推荐等级")


def plot_topic_distribution(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    data = topic_counts(frame, top_n=top_n).sort_values("项目数量")
    fig = go.Figure(
        go.Bar(
            x=data["项目数量"],
            y=data["技术主题"],
            orientation="h",
            marker={"color": np.linspace(0, 1, len(data)), "colorscale": [[0, "#BAE6FD"], [1, "#0EA5E9"]]},
            hovertemplate="技术主题：%{y}<br>项目数量：%{x}<extra></extra>",
        )
    )
    fig.update_xaxes(title="项目数量")
    fig.update_yaxes(title="技术主题")
    return apply_streamlit_plotly_theme(fig, height=max(420, top_n * 26))


def plot_risk_potential(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    colors = {"A": "#0EA5E9", "B": "#38BDF8", "C": "#93C5FD", "D": "#CBD5E1"}
    for level in ["A", "B", "C", "D"]:
        sub = frame[frame["recommendation_level"] == level]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["risk_score"],
                y=sub["final_potential_score"],
                mode="markers",
                name=display_level(level),
                hovertext=sub["full_name"],
                customdata=np.column_stack(
                    [
                        sub["full_name"],
                        sub["language"].fillna("Unknown"),
                        sub["risk_score"].round(2),
                        sub["final_potential_score"].round(2),
                        sub["repo_url"].fillna(""),
                    ]
                ),
                marker={"size": 11, "color": colors[level], "opacity": 0.75, "line": {"color": "#FFFFFF", "width": 0.8}},
                hovertemplate=format_hover_template(
                    [("仓库", ""), ("语言", ""), ("风险分", ":.2f"), ("综合潜力分", ":.2f"), ("GitHub", "")]
                ),
            )
        )
    fig.add_hline(y=float(frame["final_potential_score"].median()), line_dash="dot", line_color="#93C5FD")
    fig.add_vline(x=float(frame["risk_score"].median()), line_dash="dot", line_color="#FDBA74")
    fig.update_xaxes(title="风险分")
    fig.update_yaxes(title="综合潜力分")
    return apply_streamlit_plotly_theme(fig, height=520, legend_title="推荐等级")


def plot_personalized(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for level, color in {"A": "#0EA5E9", "B": "#38BDF8", "C": "#93C5FD", "D": "#CBD5E1"}.items():
        sub = frame[frame["recommendation_level"] == level]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["final_potential_score"],
                y=sub["personalized_score"],
                mode="markers",
                name=display_level(level),
                hovertext=sub["full_name"],
                customdata=np.column_stack(
                    [
                        sub["full_name"],
                        sub["language"].fillna("Unknown"),
                        sub["final_potential_score"].round(2),
                        sub["personalized_score"].round(2),
                        sub["risk_score"].round(2),
                        sub["repo_url"].fillna(""),
                    ]
                ),
                marker={"size": 13, "color": color, "opacity": 0.75, "line": {"color": "#FFFFFF", "width": 0.8}},
                hovertemplate=format_hover_template(
                    [("仓库", ""), ("语言", ""), ("通用潜力分", ":.2f"), ("个性化匹配分", ":.2f"), ("风险分", ":.2f"), ("GitHub", "")]
                ),
            )
        )
    fig.update_xaxes(title="通用潜力分")
    fig.update_yaxes(title="个性化匹配分")
    return apply_streamlit_plotly_theme(fig, height=510, legend_title="推荐等级")


def plot_personalized_top(frame: pd.DataFrame, top_n: int = 15) -> go.Figure:
    data = frame.sort_values("personalized_score", ascending=False).head(top_n).copy()
    data["项目简称"] = data["full_name"].map(repo_short)
    data = data.sort_values("personalized_score")
    fig = go.Figure(
        go.Bar(
            x=data["personalized_score"],
            y=data["项目简称"],
            orientation="h",
            marker={"color": np.linspace(0, 1, len(data)), "colorscale": [[0, "#BAE6FD"], [1, "#0EA5E9"]]},
            customdata=np.column_stack([data["full_name"], data["personalized_score"].round(2), data["repo_url"].fillna("")]),
            hovertemplate="仓库：%{customdata[0]}<br>个性化匹配分：%{customdata[1]:.2f}<br>GitHub：%{customdata[2]}<extra></extra>",
        )
    )
    fig.update_xaxes(title="个性化匹配分")
    fig.update_yaxes(title="项目简称")
    return apply_streamlit_plotly_theme(fig, height=500)


def plot_cluster_map(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    clusters = sorted(frame["cluster_name"].dropna().unique().tolist())
    colors = blue_sequence()
    for idx, cluster in enumerate(clusters):
        sub = frame[frame["cluster_name"] == cluster]
        fig.add_trace(
            go.Scatter(
                x=sub["pca_x"],
                y=sub["pca_y"],
                mode="markers",
                name=display_cluster(cluster),
                hovertext=sub["full_name"],
                customdata=np.column_stack(
                    [
                        sub["full_name"],
                        sub["language"].fillna("Unknown"),
                        sub["final_potential_score"].round(2),
                        sub["risk_score"].round(2),
                        sub["repo_url"].fillna(""),
                    ]
                ),
                marker={"size": 11, "color": colors[idx % len(colors)], "opacity": 0.76, "line": {"color": "#FFFFFF", "width": 0.8}},
                hovertemplate=format_hover_template(
                    [("仓库", ""), ("语言", ""), ("综合潜力分", ":.2f"), ("风险分", ":.2f"), ("GitHub", "")]
                ),
            )
        )
    fig.update_xaxes(title="PCA 第一主成分")
    fig.update_yaxes(title="PCA 第二主成分")
    return apply_streamlit_plotly_theme(fig, height=560, legend_title="项目类型")


def plot_cluster_counts(frame: pd.DataFrame) -> go.Figure:
    data = frame["cluster_name"].map(display_cluster).value_counts().sort_values().reset_index()
    data.columns = ["项目类型", "项目数量"]
    fig = go.Figure(
        go.Bar(
            x=data["项目数量"],
            y=data["项目类型"],
            orientation="h",
            marker={"color": np.linspace(0, 1, len(data)), "colorscale": [[0, "#BAE6FD"], [1, "#0EA5E9"]]},
            hovertemplate="项目类型：%{y}<br>项目数量：%{x}<extra></extra>",
        )
    )
    fig.update_xaxes(title="项目数量")
    fig.update_yaxes(title="项目类型")
    return apply_streamlit_plotly_theme(fig, height=max(360, len(data) * 42))


def plot_model_comparison(metrics: pd.DataFrame, title: str) -> go.Figure:
    if metrics.empty:
        return go.Figure()
    data = metrics.copy()
    data["模型"] = data["model_name"].map(display_model)
    fig = go.Figure()
    metric_map = {"accuracy": "准确率", "precision": "精确率", "recall": "召回率", "f1": "F1 分数"}
    for idx, (col, label) in enumerate(metric_map.items()):
        if col not in data:
            continue
        fig.add_trace(
            go.Bar(
                x=data["模型"],
                y=data[col],
                name=label,
                marker_color=blue_sequence()[idx],
                hovertemplate=f"模型：%{{x}}<br>{label}：%{{y:.3f}}<extra></extra>",
            )
        )
    fig.update_layout(barmode="group")
    fig.update_xaxes(title="模型")
    fig.update_yaxes(title="指标值", range=[0, 1])
    return apply_streamlit_plotly_theme(fig, height=460, legend_title=title)


def plot_feature_importance(importance: pd.DataFrame, task: str | None = None) -> go.Figure:
    data = importance.copy()
    if task and "task" in data.columns:
        data = data[data["task"] == task].copy()
    data = data.sort_values("abs_importance", ascending=False).head(18).copy()
    data["特征"] = data["feature"].map(display_feature)
    data = data.sort_values("abs_importance")
    fig = go.Figure(
        go.Bar(
            x=data["abs_importance"],
            y=data["特征"],
            orientation="h",
            marker_color="#38BDF8",
            hovertemplate="特征：%{y}<br>重要性：%{x:.4f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="重要性")
    fig.update_yaxes(title="特征")
    return apply_streamlit_plotly_theme(fig, height=540)


def plot_torch_history(history: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if "train_loss" in history:
        fig.add_trace(go.Scatter(x=history["epoch"], y=history["train_loss"], mode="lines+markers", name="训练损失", line={"color": "#38BDF8"}))
    if "valid_loss" in history:
        fig.add_trace(go.Scatter(x=history["epoch"], y=history["valid_loss"], mode="lines+markers", name="验证损失", line={"color": "#60A5FA"}))
    if "valid_auc" in history:
        fig.add_trace(go.Scatter(x=history["epoch"], y=history["valid_auc"], mode="lines+markers", name="验证 AUC", yaxis="y2", line={"color": "#0284C7"}))
    if "valid_f1" in history:
        fig.add_trace(go.Scatter(x=history["epoch"], y=history["valid_f1"], mode="lines+markers", name="验证 F1", yaxis="y2", line={"color": "#0EA5E9"}))
    fig.update_layout(yaxis2={"overlaying": "y", "side": "right", "range": [0, 1], "title": "AUC / F1"})
    fig.update_xaxes(title="训练轮次")
    fig.update_yaxes(title="损失")
    return apply_streamlit_plotly_theme(fig, height=460, legend_title="训练指标")


def render_score_explorer(frame: pd.DataFrame, key: str) -> None:
    """Render a full-width seven-dimension score explorer before project cards."""
    if frame.empty:
        st.info("当前筛选范围内暂无项目。")
        return
    options = frame.sort_values("final_potential_score", ascending=False)["full_name"].drop_duplicates().head(100).tolist()
    selected = st.selectbox("查看单项目评分构成", options, key=key)
    row = frame[frame["full_name"] == selected].iloc[0]
    url = project_url(row)
    title = f"<a href='{html_escape(url)}' target='_blank'>{html_escape(selected)}</a>" if url else html_escape(selected)
    st.markdown(
        f"<div class='ar-card'><h3>{title}</h3><p>{badge(display_level(row.get('recommendation_level')))} {badge(display_cluster(row.get('cluster_name')), 'fog')}</p></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    score_items = list(SCORE_LABELS.items())
    with left:
        for col, label in score_items[:4]:
            progress_bar(label, pct(row.get(col)), warning=col == "risk_score")
    with right:
        for col, label in score_items[4:]:
            progress_bar(label, pct(row.get(col)), warning=col == "risk_score")


def render_recommendation_explorer(frame: pd.DataFrame, profile: Any, key: str) -> None:
    """Render the recommendation explanation before the recommendation wall."""
    if frame.empty:
        st.info("当前画像下暂无推荐结果。")
        return
    selected = st.selectbox("查看推荐解释", frame["full_name"].head(50).tolist(), key=key)
    row = frame[frame["full_name"] == selected].iloc[0]
    explanation = explain_personalized_match(row, profile)
    url = project_url(row)
    title = f"<a href='{html_escape(url)}' target='_blank'>{html_escape(selected)}</a>" if url else html_escape(selected)
    st.markdown(f"<div class='ar-card'><h3>{title}</h3></div>", unsafe_allow_html=True)
    text_card("为什么适合你", " ".join(clean_sentence(item) for item in explanation["match_reasons"]))
    text_card("推荐理由", f"该项目与当前目标和偏好匹配，个性化匹配分为 {pct(row.get('personalized_score')):.2f}，通用潜力分为 {pct(row.get('final_potential_score')):.2f}。", tone="fog")
    text_card("风险提示", " ".join(clean_sentence(item) for item in explanation["risk_warnings"]), tone="orange")
    text_card("三天复现路线", " ".join(clean_sentence(item) for item in explanation["three_day_plan"]), tone="fog")
    st.markdown(f"<div class='code-box'>{html_escape(explanation['codex_prompt'])}</div>", unsafe_allow_html=True)


def render_model_task(title: str, description: str, metrics: pd.DataFrame, importance: pd.DataFrame, task: str) -> None:
    """Render one supervised task with its own metrics and feature explanation."""
    page_header(title, description)
    if metrics.empty:
        st.info("该任务尚未生成模型指标。")
        return
    best = metrics.sort_values("f1", ascending=False).iloc[0]
    render_metric_grid(
        [
            ("最佳模型", display_model(best.get("model_name")), "按 F1 分数选择"),
            ("F1 分数", f"{best.get('f1', 0):.3f}", "综合精确率与召回率"),
            ("ROC AUC", f"{best.get('roc_auc', 0):.3f}", "排序区分能力"),
            ("Brier 分数", f"{best.get('brier_score_loss', 0):.3f}", "概率校准误差"),
        ],
        columns=4,
    )
    chart_card(f"{title}模型对比", "比较不同算法在该任务上的分类与排序表现。")
    st.plotly_chart(plot_model_comparison(metrics, title), width="stretch")
    view = metrics.copy()
    view["模型"] = view["model_name"].map(display_model)
    columns = ["模型", "accuracy", "precision", "recall", "f1", "roc_auc"]
    view = view[[col for col in columns if col in view]].rename(columns={"accuracy": "准确率", "precision": "精确率", "recall": "召回率", "f1": "F1 分数", "roc_auc": "AUC"})
    st.dataframe(view, width="stretch", hide_index=True)
    task_importance = importance[importance["task"] == task] if "task" in importance.columns else importance
    if not task_importance.empty:
        chart_card(f"{title}特征重要性", "观察该任务主要依赖哪些仓库特征形成判断。")
        st.plotly_chart(plot_feature_importance(task_importance), width="stretch")


def render_readme_signals(row: pd.Series) -> None:
    """Render README evidence as a stable two-row, three-column signal grid."""
    items = [
        ("安装说明", "已发现安装或部署说明" if int(row.get("has_install_section", 0) or 0) else "未发现明确安装说明"),
        ("快速开始", "包含快速开始信号" if int(row.get("has_quickstart", 0) or 0) else "快速开始信号较弱"),
        ("示例说明", "包含示例或演示信号" if int(row.get("has_example", 0) or 0) else "示例信号较弱"),
        ("依赖说明", "包含依赖说明" if int(row.get("has_requirements", 0) or 0) else "依赖说明需要人工确认"),
        ("运行提示", "README 提到 GPU 或密钥要求" if int(row.get("mentions_gpu", 0) or 0) or int(row.get("mentions_api_key", 0) or 0) else "未发现明显高门槛运行提示"),
        ("文档规模", f"README 约 {int(row.get('readme_length', 0) or 0):,} 字符"),
    ]
    cards = "".join(f"<div class='readme-signal'><b>{html_escape(label)}</b><span>{html_escape(value)}</span></div>" for label, value in items)
    st.markdown(f"<div class='readme-signal-grid'>{cards}</div>", unsafe_allow_html=True)


config = read_config_without_env()
scored_path = config.get("paths", {}).get("scored_repos", "data/processed/scored_repos.csv")
if not project_path(scored_path).exists():
    st.warning("未找到处理后的项目数据。请先运行 python main.py 生成分析结果。")
    st.stop()

df = read_csv(scored_path)
run_summary = read_json("outputs/reports/run_summary.json")
collection_log = read_json("data/raw/api_collection_log.json")
agent_records = load_agent_records()
personalized_saved = read_csv("outputs/reports/personalized_recommendations.csv")
torch_metrics = read_json("outputs/reports/torch_model_metrics.json")

with st.sidebar:
    st.markdown("### 用户画像")
    with st.form("profile_form"):
        saved_profile = build_user_profile_from_dict(st.session_state.get("profile"))
        profile_payload = {
            "user_role": st.selectbox("身份角色", ROLE_OPTIONS, index=ROLE_OPTIONS.index(saved_profile.user_role)),
            "main_goal": st.selectbox("主要目标", GOAL_OPTIONS, index=GOAL_OPTIONS.index(saved_profile.main_goal)),
            "programming_level": st.selectbox("编程水平", LEVEL_OPTIONS, index=LEVEL_OPTIONS.index(saved_profile.programming_level)),
            "preferred_languages": st.multiselect("偏好语言", LANGUAGE_OPTIONS, default=saved_profile.preferred_languages),
            "preferred_topics": st.multiselect("偏好主题", TOPIC_OPTIONS, default=saved_profile.preferred_topics),
            "hardware_condition": st.selectbox("运行条件", HARDWARE_OPTIONS, index=HARDWARE_OPTIONS.index(display_hardware(saved_profile.hardware_condition))),
            "risk_preference": st.selectbox("风险偏好", RISK_OPTIONS, index=RISK_OPTIONS.index(saved_profile.risk_preference)),
            "output_preference": st.multiselect("输出偏好", OUTPUT_OPTIONS, default=saved_profile.output_preference),
        }
        submitted_profile = st.form_submit_button("保存画像")
    if submitted_profile:
        st.session_state["profile"] = build_user_profile_from_dict(profile_payload).to_dict()
        st.session_state["profile_complete"] = True

    pages = [
        "首页 / 项目概览", "数据采集", "指标体系", "趋势洞察", "评分排行", "聚类画像", "模型预测",
        "PyTorch 扩展", "个性化推荐", "DeepSeek Agent", "单项目详情", "项目亮点", "局限展望", "报告导出",
    ]
    page = st.radio("导航", pages, label_visibility="collapsed", key="main_navigation")

profile = build_user_profile_from_dict(st.session_state.get("profile"))

st.markdown(
    f"""
<div class="ar-hero">
  <h1>AgentRadar-Stat</h1>
  <div class="subtitle">AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台</div>
  <p>以 GitHub 公开仓库为主数据源，构建从采集、建模到个性化推荐和 Agent 解释的完整闭环。</p>
  <div class="tag-row">
    <span class="ar-badge">{len(df)} 个 GitHub 公开仓库</span><span class="ar-badge">多模型评分</span>
    <span class="ar-badge">聚类画像</span><span class="ar-badge">PyTorch 表格神经网络</span>
    <span class="ar-badge">个性化推荐</span><span class="ar-badge">DeepSeek Agent 解释</span>
    <span class="ar-badge">HTML/PDF 自动报告</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if page == "首页 / 项目概览":
    page_header("项目概览", "从真实仓库样本出发，串联特征建模、预测扩展、智能决策与报告交付。")
    st.markdown(capability_flow(), unsafe_allow_html=True)
    high_risk = int((df["risk_score"] >= df["risk_score"].quantile(0.80)).sum()) if "risk_score" in df else 0
    cluster_count = int(df["cluster_name"].nunique()) if "cluster_name" in df else int(run_summary.get("best_k", 0) or 0)
    metrics = [
        ("GitHub 仓库样本", len(df), "用于评分与建模的项目集合"),
        ("扩展关键词", len(run_summary.get("requested_keywords", [])) or 34, "覆盖 Agent 生态方向"),
        ("去重后仓库", run_summary.get("repos_after_dedup", collection_log.get("repos_after_dedup", "—")), "按仓库全名合并"),
        ("入模项目", len(df), "进入评分和模型流程"),
        ("A 级推荐项目", int((df["recommendation_level"] == "A").sum()), "优先关注候选"),
        ("高风险项目", high_risk, "风险分前 20% 项目"),
        ("聚类画像", f"{cluster_count} 类", "项目结构画像"),
        ("监督任务", "任务 A / B", "评分解释与潜力代理预测"),
        ("机器学习模型", "6 类", "线性、树模型与集成模型"),
        ("表格宽深神经网络", "TabularWideDeepNet", "深度学习扩展实验"),
        ("个性化推荐", len(personalized_saved) or 20, "画像匹配输出"),
        ("DeepSeek Agent", len(agent_records) or 7, "解释与审查卡片"),
    ]
    render_metric_grid(metrics, columns=4)
    page_header("精选项目卡片墙", "综合潜力靠前的项目构成快速选题入口，可先查看七维评分再浏览项目卡片。")
    render_score_explorer(df, "home_score_explorer")
    render_project_cards(df, top_n=12)

elif page == "数据采集":
    page_header("数据采集", "本页展示 GitHub 公开仓库生态样本从关键词搜索、种子仓库补充、去重过滤到特征入模的形成过程，体现数据来源、筛选逻辑与样本构建的可复核性。")
    sample_metrics = [
        ("关键词搜索候选", collection_log.get("raw_items_before_dedup", run_summary.get("raw_items_before_dedup", "—")), "多关键词、多排序候选"),
        ("去重后仓库", collection_log.get("repos_after_dedup", run_summary.get("repos_after_dedup", "—")), "按仓库全名去重"),
        ("相关性过滤后", collection_log.get("repos_after_relevance_filter", run_summary.get("repos_after_relevance_filter", "—")), "保留 Agent 相关信号"),
        ("最终入模项目", len(df), "进入评分、聚类和推荐"),
    ]
    render_metric_grid(sample_metrics, columns=4)
    funnel_values = [int(collection_log.get("raw_items_before_dedup", len(df)) or len(df)), int(collection_log.get("repos_after_dedup", len(df)) or len(df)), int(collection_log.get("repos_after_relevance_filter", len(df)) or len(df)), len(df)]
    fig = go.Figure(go.Funnel(y=["关键词搜索候选", "去重后仓库", "相关性过滤后", "最终入模项目"], x=funnel_values, marker={"color": blue_sequence()[:4]}))
    fig.update_traces(hovertemplate="阶段：%{y}<br>项目数量：%{x}<extra></extra>")
    chart_card("数据采集漏斗", "呈现候选仓库经过去重和相关性过滤后形成建模样本的过程。")
    st.plotly_chart(apply_streamlit_plotly_theme(fig, height=440), width="stretch")
    st.markdown("<div class='ar-card'><h4>样本构建路径说明</h4><p>关键词覆盖 Agent、RAG、MCP、Coding、Workflow 等方向；多排序策略覆盖 Stars、更新时间、Forks 与最佳匹配；seed 仓库补充高相关项目；按仓库全名去重后，再依据名称、简介、主题与 README 信号完成相关性过滤并进入模型。</p></div>", unsafe_allow_html=True)
    with st.expander("高级诊断", expanded=False):
        diag = pd.DataFrame([{"指标": "搜索关键词数量", "数值": len(collection_log.get("requested_keywords", []))}, {"指标": "搜索策略数量", "数值": len(collection_log.get("search_strategies", []))}, {"指标": "README 抓取上限", "数值": collection_log.get("max_readme_repos", "—")}, {"指标": "智能体分析上限", "数值": config.get("collection", {}).get("max_agent_repos", "—")}])
        st.dataframe(diag, width="stretch", hide_index=True)

elif page == "指标体系":
    page_header("指标体系", "指标体系把开源项目的热度、维护活跃、社区参与、文档质量、技术创新、复现可行性与风险惩罚整合为统一评价框架，避免仅按 Stars 排序。")
    score_cards = [("趋势热度", "衡量项目关注度与增长信号。"), ("活跃维护", "衡量维护节奏与问题处理状态。"), ("社区参与", "衡量派生开发与社区互动。"), ("文档质量", "衡量安装、示例与依赖说明。"), ("技术创新", "衡量 Agent、RAG、MCP 与工作流信号。"), ("复现可行", "衡量快速开始、演示与运行门槛。"), ("风险惩罚", "综合维护停滞、问题压力与复现复杂度。")]
    render_metric_grid([(title, f"0-100", note) for title, note in score_cards], columns=4)
    st.markdown("<div class='ar-card'><h4>综合评价逻辑</h4><p><b>通用潜力</b>由热度、维护、社区、文档、创新和复现信号共同形成，再结合风险惩罚校正；<b>个性化匹配</b>进一步叠加目标、语言、主题、风险偏好与输出偏好，使同一项目对不同用户呈现不同优先级。</p></div>", unsafe_allow_html=True)
    page_header("个性化匹配机制", "用户画像只用于本地偏好匹配，不包含身份凭据或敏感信息。")
    render_metric_grid([("用户画像", "本地偏好", "目标与学习阶段"), ("语言偏好", "技术栈", "匹配主要编程语言"), ("主题偏好", "方向", "匹配 Coding、RAG、MCP 等主题"), ("风险偏好", "约束", "调整探索与稳健项目权重"), ("输出偏好", "交付", "适配排行榜、路线与解释")], columns=5)

elif page == "趋势洞察":
    page_header("趋势洞察", "观察 AI Agent 相关项目的语言生态、关注度长尾分布、派生开发活跃关系和技术主题结构。")
    c1, c2 = st.columns([2, 1])
    top_n = c1.slider("展示数量", 5, min(100, len(df)), min(20, len(df)))
    scope_mode = c2.radio("统计范围", ["当前展示数量", "全量样本"], horizontal=True)
    ranked = df.sort_values("final_potential_score", ascending=False)
    scope_df = ranked.head(top_n) if scope_mode == "当前展示数量" else ranked
    c1, c2 = st.columns(2)
    with c1:
        chart_card("主要编程语言分布", "观察项目复现门槛和生态主语言。")
        st.plotly_chart(plot_language_distribution(scope_df, top_n=min(12, scope_df["language"].nunique())), width="stretch")
    with c2:
        chart_card("GitHub Stars 分布特征", "观察头部项目与长尾项目差异。")
        st.plotly_chart(plot_stars_distribution(scope_df), width="stretch")
    chart_card("Stars-Forks 气泡关系", "观察关注度与派生开发活跃度。")
    st.plotly_chart(plot_stars_forks(scope_df), width="stretch")
    chart_card("技术主题分布", "观察样本中不同 AI Agent 技术方向结构。")
    st.plotly_chart(plot_topic_distribution(scope_df, top_n=min(15, max(5, len(scope_df)))), width="stretch")
    page_header("精选项目卡片墙", "当前统计范围内按综合潜力排序的项目。")
    render_score_explorer(scope_df, "trend_score_explorer")
    render_project_cards(scope_df, top_n=min(12, len(scope_df)))

elif page == "评分排行":
    page_header("评分排行", "从综合潜力与风险暴露两个角度识别值得优先关注和需要谨慎评估的项目。")
    r1c1, r1c2, r1c3 = st.columns(3)
    levels = r1c1.multiselect("推荐等级", ["A", "B", "C", "D"], default=["A", "B", "C", "D"], format_func=display_level)
    languages = sorted(df["language"].fillna("Unknown").unique().tolist())
    selected_lang = r1c2.multiselect("主要语言", languages, default=languages)
    clusters = sorted(df["cluster_name"].fillna("项目类型待识别").unique().tolist()) if "cluster_name" in df else []
    selected_clusters = r1c3.multiselect("项目类型", clusters, default=clusters, format_func=display_cluster)
    r2c1, r2c2, r2c3 = st.columns(3)
    risk_range = r2c1.slider("风险分范围", 0.0, 100.0, (0.0, 100.0))
    score_range = r2c2.slider("潜力分范围", 0.0, 100.0, (0.0, 100.0))
    top_n = r2c3.slider("项目数量", 5, 50, 20)
    view = df[df["recommendation_level"].isin(levels) & df["language"].fillna("Unknown").isin(selected_lang) & df["risk_score"].between(*risk_range) & df["final_potential_score"].between(*score_range)]
    if selected_clusters and "cluster_name" in view:
        view = view[view["cluster_name"].fillna("项目类型待识别").isin(selected_clusters)]
    chart_card("风险—潜力四象限", "将项目放在风险分与综合潜力分构成的坐标系中，帮助识别优先推荐、谨慎探索和暂不推荐的项目。")
    if not view.empty:
        st.plotly_chart(plot_risk_potential(view), width="stretch")
    page_header("项目卡片墙", "筛选结果按综合潜力排序，可先展开单项目七维评分。")
    render_score_explorer(view, "ranking_score_explorer")
    render_project_cards(view, top_n=top_n)

elif page == "聚类画像":
    page_header("聚类画像", "把仓库划分为不同项目类型，观察项目在潜力、风险和工程成熟度上的结构差异；聚类结果用于解释，不作为监督学习标签。")
    if not {"pca_x", "pca_y", "cluster_name"}.issubset(df.columns):
        st.warning("聚类结果尚未生成。请先运行 python main.py。")
    else:
        render_metric_grid([("最终聚类模型", display_model(run_summary.get("best_cluster_model", "KMeans")), "综合轮廓系数与稳定性选择"), ("最优 k", run_summary.get("best_k", df["cluster_name"].nunique()), "候选聚类数量"), ("稳定性 ARI", f"{run_summary.get('cluster_stability', {}).get('mean_ari', 0):.2f}", "多次随机种子一致性"), ("聚类类型数量", df["cluster_name"].nunique(), "展示用项目画像")], columns=4)
        chart_card("PCA / 聚类项目地图", "将多维项目特征压缩到二维空间，观察不同项目画像之间的距离和聚集关系。")
        st.plotly_chart(plot_cluster_map(df), width="stretch")
        c1, c2 = st.columns(2)
        with c1:
            chart_card("聚类类型数量", "比较不同项目画像中的仓库数量。")
            st.plotly_chart(plot_cluster_counts(df), width="stretch")
        with c2:
            comparison = read_csv("outputs/reports/cluster_model_comparison.csv")
            if not comparison.empty:
                chart_card("聚类方法比较", "比较候选算法的分离度、紧凑度与综合选择结果。")
                table = comparison.copy()
                table["模型"] = table["model"].map(display_model)
                cols = [c for c in ["模型", "k", "silhouette", "davies_bouldin", "selection_score"] if c in table.columns]
                st.dataframe(table[cols].rename(columns={"silhouette": "轮廓系数", "davies_bouldin": "DB 指数", "selection_score": "选择分"}).head(12), width="stretch", hide_index=True)
        page_header("各聚类类型代表项目", "每类按综合潜力选择代表项目，便于比较不同画像的典型特征。")
        for cluster, group in df.groupby("cluster_name"):
            st.markdown(f"<div class='ar-card'><h4>{html_escape(display_cluster(cluster))}</h4><p>该类型包含 {len(group)} 个项目，以下展示综合潜力靠前的代表项目。</p></div>", unsafe_allow_html=True)
            render_project_cards(group, top_n=5)

elif page == "模型预测":
    page_header("模型预测", "任务 A 检验评分边界的可解释性，任务 B 观察原始仓库特征对项目潜力代理标签的预测能力。")
    st.markdown("<div class='ar-card'><h4>任务定义与防泄漏说明</h4><p><b>任务 A：</b>评分体系代理模型，用于解释当前评分边界。</p><p><b>任务 B：</b>项目潜力代理预测，用于观察原始仓库特征的解释力。</p><p>训练输入不直接使用最终评分、推荐等级和评分子项，避免把答案字段泄漏给模型。</p></div>", unsafe_allow_html=True)
    task_a = read_csv("outputs/reports/model_metrics_task_a.csv")
    task_b = read_csv("outputs/reports/model_metrics_task_b.csv")
    importance = read_csv("outputs/reports/feature_importance.csv")
    tab_a, tab_b = st.tabs(["任务 A：评分体系代理模型", "任务 B：项目潜力代理预测"])
    with tab_a:
        render_model_task("任务 A：评分体系代理模型", "检验评分体系边界能否由未泄漏的仓库特征解释。", task_a, importance, "task_a")
    with tab_b:
        render_model_task("任务 B：项目潜力代理预测", "观察原始仓库特征对潜力代理标签的分类与排序能力。", task_b, importance, "task_b")

elif page == "PyTorch 扩展":
    page_header("PyTorch 扩展", "表格宽深神经网络把数值特征、类别特征和线性记忆分支组合起来，作为传统机器学习之外的扩展实验。")
    st.markdown("<div class='ar-card'><h4>表格宽深神经网络</h4><div class='capability-flow' style='grid-template-columns:repeat(4,minmax(0,1fr))'><div class='capability-stage'><b>数值分支</b><span class='capability-node'>仓库统计特征</span><span class='capability-node'>README 信号</span></div><div class='capability-stage'><b>类别分支</b><span class='capability-node'>语言嵌入</span><span class='capability-node'>项目画像嵌入</span></div><div class='capability-stage'><b>宽深融合</b><span class='capability-node'>线性记忆</span><span class='capability-node'>非线性交互</span></div><div class='capability-stage'><b>输出层</b><span class='capability-node'>潜力代理预测</span><span class='capability-node'>概率校准参考</span></div></div></div>", unsafe_allow_html=True)
    torch_history = read_csv("outputs/reports/torch_training_history.csv")
    chart_card("PyTorch 表格宽深神经网络训练曲线", "训练曲线用于观察模型收敛过程和验证集表现。")
    if not torch_history.empty:
        st.plotly_chart(plot_torch_history(torch_history), width="stretch")
    render_metric_grid([("验证 AUC", f"{torch_metrics.get('valid_auc', 0):.3f}", "验证集排序能力"), ("验证 F1", f"{torch_metrics.get('valid_f1', 0):.3f}", "验证集综合表现"), ("测试 F1", f"{torch_metrics.get('test_f1', 0):.3f}", "独立测试表现"), ("实验定位", "扩展对照", "不替代传统模型结论")], columns=4)

elif page == "个性化推荐":
    page_header("个性化推荐", "根据目标、语言偏好、主题偏好和风险偏好，把通用项目质量转化为面向当前用户的匹配排序。")
    render_profile_summary(profile)
    personalized_df = compute_personalized_score(df, profile).sort_values("personalized_score", ascending=False)
    chart_card("个性化匹配分与通用潜力分", "比较通用项目质量与当前用户画像之间的匹配差异。")
    st.plotly_chart(plot_personalized(personalized_df.head(160)), width="stretch")
    chart_card("个性化推荐 Top 15", "展示当前画像下最值得优先查看的项目。")
    st.plotly_chart(plot_personalized_top(personalized_df, top_n=15), width="stretch")
    page_header("个性化项目卡片墙", "先查看推荐解释，再按个性化匹配分浏览候选项目。")
    render_recommendation_explorer(personalized_df, profile, "personalized_explorer")
    render_project_cards(personalized_df, top_n=15, sort_by="personalized_score", personalized=True)
    popular = personalized_df.sort_values("final_potential_score", ascending=False).head(25).copy()
    popular["score_gap"] = popular["final_potential_score"] - popular["personalized_score"]
    page_header("热门但不适合当前画像", "这些项目通用评分较高，但与当前目标或偏好存在匹配差距。")
    render_project_table(popular.sort_values("score_gap", ascending=False), top_n=8, sort_by="score_gap", ascending=False)

elif page == "DeepSeek Agent":
    page_header("DeepSeek Agent", "七个智能体把仓库字段、图表和模型结果转化为自然中文解释，并保留事实依据与风险边界。")
    if not agent_records:
        st.info("尚未生成智能体解释。请先运行 python main.py。")
    for record in agent_records:
        render_agent_showcase(record)

elif page == "单项目详情":
    page_header("单项目详情", "选择任一仓库，查看基础信息、七维评分、README 信号与项目解释。")
    search = st.text_input("搜索仓库", "")
    candidates = df[df["full_name"].str.contains(search, case=False, na=False)] if search else df
    if candidates.empty:
        st.info("没有匹配的仓库，请更换关键词。")
        st.stop()
    selected = st.selectbox("选择项目", candidates["full_name"].head(200).tolist())
    row = df[df["full_name"] == selected].iloc[0]
    url = project_url(row)
    st.markdown(f"<div class='ar-card'><h3>{html_escape(row['full_name'])}</h3><p>{badge(display_level(row.get('recommendation_level')))} {badge(display_cluster(row.get('cluster_name')), 'fog')} {badge(project_topic(row), 'blue')}</p><p>{'<a href=' + html_escape(url) + ' target=_blank>打开 GitHub 仓库</a>' if url else '暂无仓库链接'}</p></div>", unsafe_allow_html=True)
    render_metric_grid([("主要语言", row.get("language", "Unknown"), "项目主语言"), ("Stars", f"{int(row.get('stars_total', 0) or 0):,}", "关注度"), ("Forks", f"{int(row.get('forks_total', 0) or 0):,}", "派生活跃"), ("Open Issues", int(row.get("open_issues_count", 0) or 0), "问题压力参考")], columns=4)
    left, right = st.columns(2)
    with left:
        for col, label in list(SCORE_LABELS.items())[:4]: progress_bar(label, pct(row.get(col)), warning=col == "risk_score")
    with right:
        for col, label in list(SCORE_LABELS.items())[4:]: progress_bar(label, pct(row.get(col)), warning=col == "risk_score")
    page_header("README 信号", "从安装、示例、依赖和运行提示中判断项目复现准备度。")
    render_readme_signals(row)
    cached = load_single_project_cache(selected)
    if st.button("生成该项目解释", width="stretch"):
        st.session_state["selected_project_cache"] = cached or {"title": "ScoringAgent", "title_cn": "评分解释智能体", "role_cn": "基于当前项目数据生成可读解释。", "summary": f"{selected} 的综合潜力分为 {pct(row.get('final_potential_score')):.2f}，风险分为 {pct(row.get('risk_score')):.2f}。", "key_findings": [f"项目主题为 {project_topic(row)}，主要语言为 {safe_text(row.get('language'), 'Unknown')}。"], "evidence": ["依据来自七维评分、README 信号和项目画像。"], "risks": ["需要继续检查许可证、依赖安装和维护状态。"], "next_steps": ["优先阅读 README，跑通最小示例，再记录复现过程。"]}
    selected_cache = st.session_state.get("selected_project_cache") or cached
    if selected_cache: render_agent_showcase(selected_cache)

elif page == "项目亮点":
    page_header("项目亮点", "从数据来源、方法严谨性、智能解释和多形态交付四个方面总结项目工作量与成果。")
    highlights = [("真实生态样本", "GitHub 公开仓库经过多关键词、多排序、种子补充、去重与相关性过滤形成分析样本。"), ("七维评分体系", "把热度、活跃、社区、文档、创新、复现和风险整合为统一评价框架。"), ("多算法聚类", "比较 KMeans、高斯混合、层次聚类与密度聚类，形成可解释项目画像。"), ("任务 A / B 防泄漏建模", "分别检验评分边界与潜力代理预测，并排除直接答案字段。"), ("PyTorch 扩展", "以表格宽深神经网络补充传统机器学习对照实验。"), ("个性化推荐", "根据用户目标与偏好生成项目、理由、风险、三天路线和 Codex Prompt。"), ("七智能体解释", "DeepSeek Agent 负责解释、建议与事实审查，不替代数据事实。"), ("多形态交付", "同一流水线生成 Streamlit、交互式 HTML 与 PDF 项目报告。")]
    for start in range(0, len(highlights), 2):
        cols = st.columns(2)
        for col, (title, body) in zip(cols, highlights[start:start + 2]):
            with col: text_card(title, body)

elif page == "局限展望":
    page_header("局限展望", "明确数据时点、代理标签与解释层边界，并给出后续可验证的扩展方向。")
    left, right = st.columns(2)
    with left:
        text_card("研究边界", "GitHub 数据具有采集时点性；README 与主题文本可能误判；任务 A/B 使用代理标签；评分体系不等同于商业价值预测。", tone="orange")
        text_card("解释边界", "智能体输出用于组织证据和行动建议，关键结论仍需回到仓库信息、图表、模型卡和结果表核对。", tone="fog")
    with right:
        text_card("数据扩展", "可增加增量采集、时间序列跟踪、PR 与 Issue 互动质量以及真实用户反馈。")
        text_card("产品扩展", "可补充更严格的离线评测、在线部署和面向候选项目的复现脚手架生成。", tone="fog")

elif page == "报告导出":
    page_header("报告导出", "集中提供最终项目报告 PDF 与交互式 HTML 项目报告。")
    report_html = project_path("outputs/reports/agent_radar_report.html")
    report_pdf = project_path("outputs/reports/agent_radar_report.pdf")
    render_metric_grid([("PDF 项目报告", "已生成" if report_pdf.exists() else "待生成", "适合最终展示与提交"), ("HTML 项目报告", "已生成" if report_html.exists() else "待生成", "适合交互式查看")], columns=2)
    c1, c2 = st.columns(2)
    with c1:
        if report_pdf.exists():
            st.download_button("打开 / 下载项目报告 PDF", report_pdf.read_bytes(), "agent_radar_report.pdf", "application/pdf", width="stretch")
        else:
            st.warning("请先运行 python main.py 生成项目报告。")
    with c2:
        if report_html.exists():
            st.download_button("打开交互式 HTML 项目报告", report_html.read_bytes(), "agent_radar_report.html", "text/html", width="stretch")
        else:
            st.warning("请先运行 python main.py 生成项目报告。")
