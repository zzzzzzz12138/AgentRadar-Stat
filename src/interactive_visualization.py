from __future__ import annotations

import math
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .theme import COLORS, LEVEL_COLORS, PALETTE, RISK_COLORS, style_plotly


MODEL_NAME_CN = {
    "logistic_regression": "逻辑回归",
    "random_forest": "随机森林",
    "extra_trees": "极端随机树",
    "gradient_boosting": "梯度提升树",
    "hist_gradient_boosting": "直方梯度提升",
    "calibrated_classifier": "概率校准模型",
    "calibrated_random_forest": "校准随机森林",
    "dummy": "随机基线",
}

FEATURE_NAME_CN = {
    "agent_relevance_score": "AI Agent 相关性",
    "has_demo": "是否包含 Demo",
    "has_requirements": "是否包含依赖说明",
    "readme_length": "README 长度",
    "days_since_update": "距上次更新天数",
    "log_stars": "Stars 对数",
    "log_forks": "Forks 对数",
    "topic_count": "Topic 数量",
    "issue_pressure": "Issue 压力",
    "reproducibility_score": "复现可行分",
    "documentation_score": "文档质量分",
    "activity_score": "活跃维护分",
    "community_score": "社区参与分",
    "innovation_score": "技术创新分",
    "feasibility_score": "复现可行分",
    "trend_score": "趋势热度分",
    "stars_total": "Stars",
    "forks_total": "Forks",
    "watchers_total": "Watchers",
    "open_issues_count": "Open Issues",
    "mentions_cpu": "提及 CPU",
    "mentions_gpu": "提及 GPU",
    "mentions_docker": "提及 Docker",
    "mentions_api_key": "密钥配置提示",
    "mentions_requirements": "依赖说明提示",
    "mentions_quickstart": "快速开始提示",
    "mentions_example": "示例代码提示",
    "has_quickstart": "是否包含快速开始",
    "has_example": "是否包含示例",
    "stars_per_day": "日均 Stars",
    "forks_per_star": "Fork 转化率",
    "project_age_days": "项目年龄",
    "description_length": "简介长度",
    "topics_signal_count": "主题信号数量",
    "api_signal_count": "接口信号数量",
    "readme_signal_count": "README 信号数量",
    "size": "仓库体量",
    "owner_type": "所有者类型",
    "language_encoded": "语言类别",
    "cluster_label": "画像类别编号",
}

TOPIC_BUCKETS = {
    "智能体框架": ["agent", "agents", "ai-agent", "llm-agent", "autonomous"],
    "MCP工具生态": ["mcp", "model-context-protocol"],
    "检索增强生成": ["rag", "retrieval", "vector", "embedding"],
    "编程智能体": ["coding", "code-agent", "developer", "codex", "computer-use"],
    "工作流自动化": ["workflow", "automation", "orchestration"],
    "数据智能体": ["data-agent", "data analysis", "analytics"],
    "多智能体协作": ["multi-agent", "autogen", "crewai", "metagpt"],
    "本地大模型": ["local-llm", "ollama", "llama", "local llm"],
}


def plotly_script_tag() -> str:
    """Return the Plotly loader used by the showcase report."""
    return '<script src="https://cdn.plot.ly/plotly-3.0.0.min.js"></script>'


def chart_html(fig: go.Figure, height: int | None = None) -> str:
    """Render a Plotly figure as an embeddable HTML fragment."""
    if height:
        fig.update_layout(height=height)
    fig.update_layout(title={"text": ""})
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    )


def build_interactive_charts(
    scored: pd.DataFrame,
    clustered: pd.DataFrame | None = None,
    task_a: pd.DataFrame | None = None,
    task_b: pd.DataFrame | None = None,
    feature_importance: pd.DataFrame | None = None,
    torch_history: pd.DataFrame | None = None,
    personalized: pd.DataFrame | None = None,
    run_summary: dict[str, Any] | None = None,
    collection_log: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build all report Plotly fragments from current pipeline outputs."""
    df = _merge_cluster_fields(scored, clustered)
    task_a = task_a if task_a is not None else pd.DataFrame()
    task_b = task_b if task_b is not None else pd.DataFrame()
    feature_importance = feature_importance if feature_importance is not None else pd.DataFrame()
    torch_history = torch_history if torch_history is not None else pd.DataFrame()
    personalized = personalized if personalized is not None else pd.DataFrame()
    run_summary = run_summary or {}
    collection_log = collection_log or {}
    return {
        "language_distribution": chart_html(language_distribution(df), 420),
        "stars_distribution": chart_html(stars_distribution(df), 420),
        "stars_forks_bubble": chart_html(stars_forks_bubble(df), 560),
        "topic_distribution": chart_html(topic_distribution(df), 430),
        "top_potential": chart_html(top_potential(df, 20), 620),
        "top_risk": chart_html(top_risk(df, 20), 620),
        "risk_potential_quadrant": chart_html(risk_potential_quadrant(df), 650),
        "pca_cluster_map": chart_html(pca_cluster_map(df), 650),
        "cluster_type_counts": chart_html(cluster_type_counts(df), 430),
        "model_comparison": chart_html(model_comparison(task_a, task_b), 520),
        "feature_importance": chart_html(feature_importance_chart(feature_importance), 620),
        "model_comparison_task_a": chart_html(model_comparison_task(task_a, "任务 A：评分体系代理模型"), 480),
        "model_comparison_task_b": chart_html(model_comparison_task(task_b, "任务 B：项目潜力代理预测"), 480),
        "feature_importance_task_a": chart_html(feature_importance_chart(feature_importance, "task_a"), 560),
        "feature_importance_task_b": chart_html(feature_importance_chart(feature_importance, "task_b"), 560),
        "torch_training_curve": chart_html(torch_training_curve(torch_history), 480),
        "personalized_vs_base": chart_html(personalized_vs_base(personalized if not personalized.empty else df), 560),
        "top_personalized": chart_html(top_personalized(personalized, 15), 560) if not personalized.empty else "<p class='note'>暂无个性化推荐输出。</p>",
        "recommendation_donut": chart_html(recommendation_donut(df), 390),
        "collection_funnel": chart_html(collection_funnel(run_summary, collection_log), 430),
    }


def _merge_cluster_fields(scored: pd.DataFrame, clustered: pd.DataFrame | None) -> pd.DataFrame:
    df = scored.copy()
    if clustered is not None and not clustered.empty:
        for col in ["pca_x", "pca_y", "cluster_name", "cluster_label"]:
            if col not in df.columns and col in clustered.columns:
                df[col] = clustered[col]
    if "repo_url" not in df.columns:
        df["repo_url"] = df.get("html_url", "")
    df["repo_short"] = df.get("repo_name", df.get("full_name", "")).fillna(df.get("full_name", ""))
    return df


def _repo_custom_data(data: pd.DataFrame, extra: list[str] | None = None) -> list[str]:
    extra = extra or []
    base = ["repo_url", "full_name"]
    return [c for c in base + extra if c in data.columns]


def _risk_label(score: float) -> str:
    if score >= 70:
        return "高风险"
    if score >= 40:
        return "中风险"
    return "低风险"


def _project_topic_text(row: pd.Series) -> str:
    text = " ".join(str(row.get(col, "") or "").lower() for col in ["topics", "description", "full_name", "readme_text"])
    for label, terms in TOPIC_BUCKETS.items():
        if any(term in text for term in terms):
            return label
    return "综合智能体项目"


def _risk_reason(row: pd.Series) -> str:
    parts = []
    issues = float(row.get("open_issues_count", 0) or 0)
    days = float(row.get("days_since_update", 0) or 0)
    if issues >= 100:
        parts.append("Issue 压力较高")
    if days >= 180:
        parts.append("近期维护信号偏弱")
    if float(row.get("risk_score", 0) or 0) >= 70:
        parts.append("综合风险分处于高位")
    return "；".join(parts) if parts else "主要由维护活跃度、Issue 压力和复现复杂度共同决定"


def _friendly_feature_name(value: Any) -> str:
    text = str(value)
    if text in FEATURE_NAME_CN:
        return FEATURE_NAME_CN[text]
    cleaned = text.replace("_", " ").replace("-", " ").strip()
    if cleaned:
        return "模型特征：" + cleaned.title()
    return "模型特征"


def language_distribution(df: pd.DataFrame) -> go.Figure:
    data = df["language"].fillna("Unknown").replace("", "Unknown").value_counts().head(15).rename_axis("主要语言").reset_index(name="仓库数量")
    fig = px.bar(data, x="仓库数量", y="主要语言", orientation="h", color="仓库数量", color_continuous_scale=["#E0F7FF", "#38BDF8", "#0EA5E9"])
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    fig.update_traces(hovertemplate="主要语言：%{y}<br>仓库数量：%{x}<extra></extra>")
    return style_plotly(fig)


def stars_distribution(df: pd.DataFrame) -> go.Figure:
    values = df["stars_total"].fillna(0).clip(lower=0)
    bins = pd.cut(values.apply(lambda v: math.log10(v + 1)), bins=12)
    data = bins.value_counts().sort_index().reset_index()
    data.columns = ["Stars 对数区间", "仓库数量"]
    data["Stars 对数区间"] = data["Stars 对数区间"].astype(str)
    fig = px.bar(data, x="Stars 对数区间", y="仓库数量", color_discrete_sequence=["#38BDF8"])
    fig.update_traces(hovertemplate="Stars 对数区间：%{x}<br>仓库数量：%{y}<extra></extra>")
    fig.update_xaxes(title="Stars 对数分箱")
    fig.update_yaxes(title="仓库数量")
    return style_plotly(fig)


def stars_forks_bubble(df: pd.DataFrame) -> go.Figure:
    data = df.copy()
    data["stars_plot"] = data["stars_total"].fillna(0).clip(lower=0) + 1
    data["forks_plot"] = data["forks_total"].fillna(0).clip(lower=0) + 1
    data["bubble_size"] = data.get("open_issues_count", pd.Series([0] * len(data))).fillna(0).clip(lower=1).apply(math.sqrt)
    data["推荐等级"] = data.get("recommendation_level", pd.Series(["未评级"] * len(data))).fillna("未评级")
    fig = px.scatter(
        data,
        x="stars_plot",
        y="forks_plot",
        size="bubble_size",
        color="推荐等级",
        color_discrete_map=LEVEL_COLORS,
        custom_data=_repo_custom_data(data, ["language", "stars_total", "forks_total", "open_issues_count", "推荐等级"]),
        opacity=0.72,
        size_max=28,
    )
    fig.update_layout(legend_title_text="推荐等级")
    fig.update_xaxes(title="Stars（对数刻度）", type="log")
    fig.update_yaxes(title="Forks（对数刻度）", type="log")
    for value, axis in [(data["stars_plot"].quantile(0.5), "x"), (data["forks_plot"].quantile(0.5), "y")]:
        if axis == "x":
            fig.add_vline(x=value, line_dash="dot", line_color="#93C5FD")
        else:
            fig.add_hline(y=value, line_dash="dot", line_color="#93C5FD")
    fig.update_traces(
        hovertemplate=(
            "仓库名称：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>"
            "主要语言：%{customdata[2]}<br>Stars：%{customdata[3]}<br>Forks：%{customdata[4]}<br>"
            "Open Issues：%{customdata[5]}<br>推荐等级：%{customdata[6]}<br><b>点击打开 GitHub 仓库</b><extra></extra>"
        )
    )
    return style_plotly(fig)


def topic_distribution(df: pd.DataFrame) -> go.Figure:
    texts = (
        df.get("topics", pd.Series([""] * len(df))).fillna("")
        + " "
        + df.get("description", pd.Series([""] * len(df))).fillna("")
        + " "
        + df.get("full_name", pd.Series([""] * len(df))).fillna("")
    ).str.lower()
    data = pd.DataFrame(
        [{"技术主题": label, "项目数量": int(texts.apply(lambda text: any(term in text for term in terms)).sum())} for label, terms in TOPIC_BUCKETS.items()]
    ).sort_values("项目数量", ascending=True)
    fig = px.bar(data, x="项目数量", y="技术主题", orientation="h", color="项目数量", color_continuous_scale=["#E0F7FF", "#7DD3FC", "#0EA5E9"])
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(hovertemplate="技术主题：%{y}<br>项目数量：%{x}<extra></extra>")
    return style_plotly(fig)


def top_potential(df: pd.DataFrame, n: int = 20) -> go.Figure:
    data = df.sort_values("final_potential_score", ascending=False).head(n).sort_values("final_potential_score", ascending=True).copy()
    data["repo_short"] = data["full_name"].str.split("/").str[-1]
    data["项目主题"] = data.apply(_project_topic_text, axis=1)
    fig = px.bar(
        data,
        x="final_potential_score",
        y="repo_short",
        orientation="h",
        color="final_potential_score",
        labels={"final_potential_score": "综合潜力分"},
        color_continuous_scale=["#BAE6FD", "#38BDF8", "#0EA5E9"],
        text=data["final_potential_score"].map(lambda v: f"{v:.1f}"),
        custom_data=_repo_custom_data(data, ["项目主题", "stars_total", "forks_total", "risk_score"]),
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="综合潜力分")
    fig.update_yaxes(title="")
    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "完整仓库名：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>"
            "项目主题：%{customdata[2]}<br>Stars：%{customdata[3]}<br>Forks：%{customdata[4]}<br>"
            "综合潜力分：%{x:.2f}<br>风险分：%{customdata[5]:.2f}<br><b>点击打开 GitHub 仓库</b><extra></extra>"
        ),
    )
    return style_plotly(fig)


def top_risk(df: pd.DataFrame, n: int = 20) -> go.Figure:
    data = df.sort_values("risk_score", ascending=False).head(n).sort_values("risk_score", ascending=True).copy()
    data["repo_short"] = data["full_name"].str.split("/").str[-1]
    data["风险等级"] = data["risk_score"].apply(_risk_label)
    data["风险原因"] = data.apply(_risk_reason, axis=1)
    fig = px.bar(
        data,
        x="risk_score",
        y="repo_short",
        orientation="h",
        color="risk_score",
        labels={"risk_score": "风险分"},
        color_continuous_scale=["#FDBA74", "#FB923C", "#DC2626"],
        text=data["risk_score"].map(lambda v: f"{v:.1f}"),
        custom_data=_repo_custom_data(data, ["风险等级", "风险原因", "final_potential_score", "open_issues_count"]),
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="风险分")
    fig.update_yaxes(title="")
    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "完整仓库名：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>"
            "风险等级：%{customdata[2]}<br>风险原因：%{customdata[3]}<br>"
            "风险分：%{x:.2f}<br>潜力分：%{customdata[4]:.2f}<br>Open Issues：%{customdata[5]}<br>"
            "<b>点击打开 GitHub 仓库</b><extra></extra>"
        ),
    )
    return style_plotly(fig)


def risk_potential_quadrant(df: pd.DataFrame) -> go.Figure:
    x_mid = float(df["risk_score"].median()) if "risk_score" in df else 50
    y_mid = float(df["final_potential_score"].median()) if "final_potential_score" in df else 50
    data = df.copy()
    data["推荐等级"] = data.get("recommendation_level", pd.Series(["未评级"] * len(data))).fillna("未评级")
    data["项目类型"] = data.get("cluster_name", pd.Series(["未分类"] * len(data))).fillna("未分类")
    fig = px.scatter(
        data,
        x="risk_score",
        y="final_potential_score",
        color="推荐等级",
        color_discrete_map=LEVEL_COLORS,
        size=data["stars_total"].fillna(1).clip(lower=1).apply(lambda v: math.sqrt(v) + 4),
        size_max=24,
        opacity=0.70,
        custom_data=_repo_custom_data(data, ["language", "项目类型", "risk_score", "final_potential_score", "推荐等级"]),
    )
    fig.update_layout(legend_title_text="推荐等级")
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=y_mid, y1=100, fillcolor="#E0F7FF", opacity=0.26, line_width=0)
    fig.add_shape(type="rect", x0=x_mid, x1=100, y0=y_mid, y1=100, fillcolor="#DBEAFE", opacity=0.20, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=0, y1=y_mid, fillcolor="#F8FCFF", opacity=0.30, line_width=0)
    fig.add_shape(type="rect", x0=x_mid, x1=100, y0=0, y1=y_mid, fillcolor="#FEE2E2", opacity=0.12, line_width=0)
    fig.add_vline(x=x_mid, line_dash="dash", line_color="#93C5FD")
    fig.add_hline(y=y_mid, line_dash="dash", line_color="#93C5FD")
    for x, y, text in [(x_mid * 0.45, 96, "低风险高潜力"), (x_mid + (100 - x_mid) * 0.55, 96, "高潜力高风险"), (x_mid * 0.45, 8, "低风险低潜力"), (x_mid + (100 - x_mid) * 0.55, 8, "高风险低潜力")]:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False, bgcolor="rgba(255,255,255,.76)", bordercolor="#BAE6FD")
    fig.update_xaxes(title="风险分")
    fig.update_yaxes(title="综合潜力分")
    fig.update_traces(
        hovertemplate="仓库名称：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>主要语言：%{customdata[2]}<br>项目类型：%{customdata[3]}<br>风险分：%{customdata[4]:.2f}<br>综合潜力分：%{customdata[5]:.2f}<br>推荐等级：%{customdata[6]}<br><b>点击打开 GitHub 仓库</b><extra></extra>"
    )
    return style_plotly(fig)


def pca_cluster_map(df: pd.DataFrame) -> go.Figure:
    data = df.copy()
    x = "pca_x" if "pca_x" in data.columns else "risk_score"
    y = "pca_y" if "pca_y" in data.columns else "final_potential_score"
    data["项目类型"] = data.get("cluster_name", data.get("recommendation_level", pd.Series(["未分类"] * len(data)))).fillna("未分类")
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color="项目类型",
        color_discrete_sequence=PALETTE,
        opacity=0.76,
        size=data["stars_total"].fillna(1).clip(lower=1).apply(lambda v: math.sqrt(v) + 4),
        size_max=22,
        custom_data=_repo_custom_data(data, ["language", "final_potential_score", "risk_score", "项目类型"]),
    )
    fig.update_layout(legend_title_text="项目类型")
    fig.update_xaxes(title="PCA 第一主成分")
    fig.update_yaxes(title="PCA 第二主成分")
    fig.update_traces(
        hovertemplate="仓库名称：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>主要语言：%{customdata[2]}<br>综合潜力分：%{customdata[3]:.2f}<br>风险分：%{customdata[4]:.2f}<br>项目类型：%{customdata[5]}<br><b>点击打开 GitHub 仓库</b><extra></extra>"
    )
    return style_plotly(fig)


def cluster_type_counts(df: pd.DataFrame) -> go.Figure:
    label_col = "cluster_name" if "cluster_name" in df.columns else "cluster_label"
    data = df[label_col].fillna("未分类").value_counts().rename_axis("项目类型").reset_index(name="项目数量").sort_values("项目数量", ascending=True)
    fig = px.bar(data, x="项目数量", y="项目类型", orientation="h", color="项目数量", color_continuous_scale=["#E0F7FF", "#38BDF8", "#0EA5E9"])
    fig.update_layout(coloraxis_showscale=False, yaxis={"automargin": True})
    fig.update_traces(hovertemplate="项目类型：%{y}<br>项目数量：%{x}<extra></extra>")
    return style_plotly(fig)


def model_comparison(task_a: pd.DataFrame, task_b: pd.DataFrame) -> go.Figure:
    frames = []
    for task_label, df in [("任务 A：评分体系代理模型", task_a), ("任务 B：项目潜力代理预测", task_b)]:
        if df is not None and not df.empty:
            temp = df.copy()
            temp["任务"] = task_label
            temp["模型"] = temp["model_name"].map(MODEL_NAME_CN).fillna(temp["model_name"])
            frames.append(temp)
    if not frames:
        return style_plotly(go.Figure())
    data = pd.concat(frames, ignore_index=True)
    metrics = [c for c in ["f1", "roc_auc", "accuracy", "balanced_accuracy"] if c in data.columns]
    long = data.melt(id_vars=["任务", "模型"], value_vars=metrics, var_name="指标", value_name="分数")
    long["指标"] = long["指标"].map({"f1": "F1", "roc_auc": "AUC", "accuracy": "准确率", "balanced_accuracy": "平衡准确率"}).fillna(long["指标"])
    fig = px.bar(long, x="模型", y="分数", color="任务", facet_col="指标", barmode="group", color_discrete_sequence=["#0EA5E9", "#7DD3FC"])
    fig.update_layout(legend_title_text="建模任务")
    fig.update_xaxes(title="", tickangle=-18)
    fig.update_yaxes(title="分数", range=[0, 1.02])
    fig.update_traces(hovertemplate="模型：%{x}<br>分数：%{y:.3f}<extra></extra>")
    return style_plotly(fig)


def model_comparison_task(metrics: pd.DataFrame, task_label: str) -> go.Figure:
    """Render one modeling task so task A and task B remain visually distinct."""
    if metrics is None or metrics.empty:
        return style_plotly(go.Figure())
    data = metrics.copy()
    data["模型"] = data["model_name"].map(MODEL_NAME_CN).fillna(data["model_name"])
    metric_map = {"f1": "F1 分数", "roc_auc": "AUC", "accuracy": "准确率", "balanced_accuracy": "平衡准确率"}
    cols = [col for col in metric_map if col in data.columns]
    long = data.melt(id_vars=["模型"], value_vars=cols, var_name="指标", value_name="分数")
    long["指标"] = long["指标"].map(metric_map)
    fig = px.bar(long, x="模型", y="分数", color="指标", barmode="group", color_discrete_sequence=["#0EA5E9", "#38BDF8", "#7DD3FC", "#BAE6FD"])
    fig.update_layout(legend_title_text=task_label)
    fig.update_xaxes(title="", tickangle=-15)
    fig.update_yaxes(title="指标值", range=[0, 1.02])
    fig.update_traces(hovertemplate="模型：%{x}<br>指标值：%{y:.3f}<extra></extra>")
    return style_plotly(fig)


def feature_importance_chart(importance: pd.DataFrame, task: str | None = None) -> go.Figure:
    if importance is None or importance.empty:
        return style_plotly(go.Figure())
    data = importance.copy()
    if task and "task" in data.columns:
        data = data[data["task"] == task].copy()
    if data.empty:
        return style_plotly(go.Figure())
    if "abs_importance" not in data.columns and "importance" in data.columns:
        data["abs_importance"] = data["importance"].abs()
    data["特征名称"] = data["feature"].map(_friendly_feature_name)
    data = data.sort_values("abs_importance", ascending=False).head(24).sort_values("abs_importance", ascending=True)
    if "task" in data.columns:
        data["建模任务"] = data["task"].map({"task_a": "任务 A", "task_b": "任务 B"}).fillna("模型任务")
    fig = px.bar(data, x="abs_importance", y="特征名称", color="建模任务" if "建模任务" in data.columns else None, orientation="h", color_discrete_sequence=["#0EA5E9", "#7DD3FC", "#93C5FD"])
    fig.update_layout(legend_title_text="建模任务")
    fig.update_xaxes(title="重要性")
    fig.update_yaxes(title="")
    fig.update_traces(hovertemplate="特征：%{y}<br>重要性：%{x:.4f}<extra></extra>")
    return style_plotly(fig)


def torch_training_curve(history: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if history is not None and not history.empty:
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
    fig.update_traces(hovertemplate="轮次：%{x}<br>数值：%{y:.4f}<extra></extra>")
    return style_plotly(fig)


def personalized_vs_base(df: pd.DataFrame) -> go.Figure:
    if "personalized_score" not in df.columns:
        return style_plotly(go.Figure())
    data = df.copy()
    if "repo_url" not in data.columns:
        data["repo_url"] = ""
    top_names = set(data.sort_values("personalized_score", ascending=False).head(5)["full_name"].astype(str))
    data["项目分组"] = data["full_name"].astype(str).map(lambda name: "重点推荐项目" if name in top_names else "候选项目")
    data["点大小"] = data["项目分组"].map({"重点推荐项目": 24, "候选项目": 9})
    fig = px.scatter(
        data,
        x="final_potential_score",
        y="personalized_score",
        color="项目分组",
        color_discrete_map={"重点推荐项目": "#0EA5E9", "候选项目": "#BAE6FD"},
        opacity=0.75,
        size="点大小",
        size_max=24,
        custom_data=_repo_custom_data(data, ["language", "risk_score", "cluster_name"]),
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line={"dash": "dash", "color": "#0EA5E9", "width": 2})
    fig.update_layout(legend_title_text="项目分组")
    fig.update_xaxes(title="通用综合潜力分")
    fig.update_yaxes(title="个性化匹配分")
    fig.update_traces(
        hovertemplate="仓库名称：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>主要语言：%{customdata[2]}<br>风险分：%{customdata[3]:.2f}<br>项目类型：%{customdata[4]}<br>通用潜力分：%{x:.2f}<br>个性化匹配分：%{y:.2f}<br><b>点击打开 GitHub 仓库</b><extra></extra>"
    )
    return style_plotly(fig)


def top_personalized(df: pd.DataFrame, n: int = 15) -> go.Figure:
    data = df.sort_values("personalized_score", ascending=False).head(n).copy()
    if "repo_url" not in data.columns:
        data["repo_url"] = ""
    data["repo_short"] = data["full_name"].str.split("/").str[-1]
    fig = px.bar(
        data,
        x="personalized_score",
        y="repo_short",
        orientation="h",
        color="personalized_score",
        labels={"personalized_score": "个性化匹配分"},
        color_continuous_scale=["#E0F7FF", "#38BDF8", "#0EA5E9"],
        text=data["personalized_score"].map(lambda v: f"{v:.1f}"),
        custom_data=_repo_custom_data(data, ["language", "final_potential_score", "risk_score", "cluster_name"]),
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    fig.update_xaxes(title="个性化匹配分")
    fig.update_yaxes(title="")
    fig.update_traces(
        textposition="outside",
        hovertemplate="仓库名称：%{customdata[1]}<br>GitHub 链接：%{customdata[0]}<br>主要语言：%{customdata[2]}<br>通用潜力分：%{customdata[3]:.2f}<br>风险分：%{customdata[4]:.2f}<br>项目类型：%{customdata[5]}<br>个性化匹配分：%{x:.2f}<br><b>点击打开 GitHub 仓库</b><extra></extra>",
    )
    return style_plotly(fig)


def recommendation_donut(df: pd.DataFrame) -> go.Figure:
    data = df["recommendation_level"].fillna("未评级").value_counts().rename_axis("推荐等级").reset_index(name="项目数量")
    fig = px.pie(data, names="推荐等级", values="项目数量", hole=0.52, color="推荐等级", color_discrete_map=LEVEL_COLORS)
    fig.update_layout(legend_title_text="推荐等级")
    fig.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="推荐等级：%{label}<br>项目数量：%{value}<extra></extra>")
    return style_plotly(fig)


def collection_funnel(run_summary: dict[str, Any], collection_log: dict[str, Any]) -> go.Figure:
    values = [
        int(run_summary.get("raw_items_before_dedup") or collection_log.get("raw_items_before_dedup") or 0),
        int(run_summary.get("repos_after_dedup") or collection_log.get("repos_after_dedup") or 0),
        int(run_summary.get("repos_after_relevance_filter") or collection_log.get("repos_after_relevance_filter") or 0),
        int(run_summary.get("repo_count") or run_summary.get("final_api_live_count") or 0),
    ]
    labels = ["关键词搜索候选", "去重后仓库", "相关性过滤后", "最终入模项目"]
    fig = go.Figure(go.Funnel(y=labels, x=values, marker={"color": ["#0EA5E9", "#38BDF8", "#7DD3FC", "#93C5FD"]}, textinfo="value+percent initial"))
    fig.update_traces(hovertemplate="%{y}：%{x}<extra></extra>")
    return style_plotly(fig)
