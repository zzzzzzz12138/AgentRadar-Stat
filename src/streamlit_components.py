from __future__ import annotations

import html
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from .agent_display import AGENT_NAME_CN
from .ui_components import project_topic


LEVEL_LABELS = {
    "A": "A 级推荐",
    "B": "B 级关注",
    "C": "C 级观察",
    "D": "D 级谨慎",
}

CLUSTER_LABELS = {
    "成熟高热度平台": "成熟高热度平台",
    "新兴潜力工具": "新兴潜力工具",
    "文档友好型项目": "文档友好型项目",
    "高风险长尾项目": "高风险长尾项目",
}

MODEL_LABELS = {
    "logistic_regression": "逻辑回归",
    "random_forest": "随机森林",
    "calibrated_random_forest": "校准随机森林",
    "gradient_boosting": "梯度提升树",
    "extra_trees": "极端随机树",
    "hist_gradient_boosting": "直方图梯度提升",
    "kmeans": "KMeans 聚类",
    "gmm": "高斯混合聚类",
    "agglomerative": "层次聚类",
    "dbscan": "DBSCAN 密度聚类",
}

FEATURE_LABELS = {
    "log_stars": "Stars 对数热度",
    "stars_total": "累计关注度",
    "stars_this_week": "近期关注增量",
    "log_forks": "Forks 对数热度",
    "open_issues_count": "开放问题数量",
    "issue_pressure": "Issue 压力",
    "days_since_update": "距离最近维护天数",
    "stars_per_day": "日均关注增长",
    "forks_per_star": "派生活跃比例",
    "topic_count": "主题标签数量",
    "readme_length": "README 长度",
    "mentions_gpu": "提及 GPU",
    "mentions_cpu": "提及本地运行",
    "mentions_api_key": "提及密钥配置",
    "mentions_docker": "提及 Docker",
    "agent_keyword_count": "Agent 关键词密度",
    "agent_relevance_score": "Agent 相关性得分",
    "reproducibility_score": "复现友好度",
    "has_demo": "演示说明信号",
    "has_install_section": "安装说明信号",
    "has_quickstart": "快速开始信号",
    "has_example": "示例说明信号",
    "archived": "归档状态",
    "size": "仓库体量",
}

SCORE_LABELS = {
    "trend_score": "趋势热度",
    "activity_score": "活跃维护",
    "community_score": "社区参与",
    "documentation_score": "文档质量",
    "innovation_score": "技术创新",
    "feasibility_score": "复现可行",
    "risk_score": "风险惩罚",
}

LEGACY_LOCAL_HARDWARE = "CPU" + "-only"
HARDWARE_DISPLAY = {
    LEGACY_LOCAL_HARDWARE: "本地普通电脑",
    "有普通 GPU": "有独立显卡",
    "有较强 GPU": "有独立显卡",
    "云端资源可用": "云端资源可用",
    "不确定": "不确定",
    "本地普通电脑": "本地普通电脑",
    "有独立显卡": "有独立显卡",
}


def safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value)
    if text.lower() == "nan":
        return default
    return text


def display_hardware(value: Any) -> str:
    return HARDWARE_DISPLAY.get(safe_text(value), safe_text(value, "本地普通电脑"))


def display_level(value: Any) -> str:
    return LEVEL_LABELS.get(safe_text(value), safe_text(value, "未分级"))


def display_cluster(value: Any) -> str:
    return CLUSTER_LABELS.get(safe_text(value), safe_text(value, "项目类型待识别"))


def display_model(value: Any) -> str:
    return MODEL_LABELS.get(safe_text(value), safe_text(value, "模型"))


def display_feature(value: Any) -> str:
    return FEATURE_LABELS.get(safe_text(value), safe_text(value, "特征"))


def badge(label: Any, tone: str = "blue") -> str:
    colors = {
        "blue": ("#E0F7FF", "#075985", "#BAE6FD"),
        "fog": ("#EFF6FF", "#1D4ED8", "#BFDBFE"),
        "orange": ("#FFF7ED", "#C2410C", "#FDBA74"),
        "slate": ("#F8FAFC", "#334155", "#CBD5E1"),
    }
    bg, color, border = colors.get(tone, colors["blue"])
    return (
        f"<span class='ar-badge' style='background:{bg};color:{color};border-color:{border}'>"
        f"{html.escape(safe_text(label))}</span>"
    )


def metric_card(label: str, value: Any, note: str = "") -> str:
    value_text = safe_text(value)
    sub = ""
    if "|" in value_text:
        value_text, sub = [part.strip() for part in value_text.split("|", 1)]
    sub_html = f'<span class="subvalue">{html.escape(sub)}</span>' if sub else ""
    return (
        "<div class='metric-card'>"
        f"<div class='label'>{html.escape(label)}</div>"
        f"<div class='value'>{html.escape(value_text)}</div>"
        f"{sub_html}"
        f"<div class='note'>{html.escape(note)}</div>"
        "</div>"
    )


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"<div class='ar-page-title'><h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p></div>",
        unsafe_allow_html=True,
    )


def chart_card(title: str, note: str = "") -> None:
    st.markdown(
        f"<div class='chart-card'><h4>{html.escape(title)}</h4><p>{html.escape(note)}</p></div>",
        unsafe_allow_html=True,
    )


def text_card(title: str, body: str, *, tone: str = "blue") -> None:
    st.markdown(
        f"<div class='text-card'>{badge(title, tone)}<p style='margin-top:10px'>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def render_metric_grid(items: list[tuple[str, Any, str]], columns: int = 4) -> None:
    for chunk_start in range(0, len(items), columns):
        cols = st.columns(columns)
        for col, item in zip(cols, items[chunk_start : chunk_start + columns]):
            with col:
                st.markdown(metric_card(*item), unsafe_allow_html=True)


def capability_flow() -> str:
    stages = [
        ("数据入口", ["GitHub 公开仓库", "关键词搜索", "seed 仓库补充"]),
        ("特征建模", ["清洗特征", "七维评分", "聚类画像"]),
        ("预测扩展", ["任务 A / B", "sklearn 模型", "PyTorch 表格宽深神经网络"]),
        ("智能决策", ["用户画像", "个性化推荐", "DeepSeek Agent 解释"]),
        ("交付形态", ["HTML 报告", "PDF 报告", "Streamlit 交互入口"]),
    ]
    cards = []
    for title, nodes in stages:
        node_html = "".join(f"<span class='capability-node'>{html.escape(node)}</span>" for node in nodes)
        cards.append(f"<div class='capability-stage'><b>{html.escape(title)}</b>{node_html}</div>")
    return "<div class='capability-flow'>" + "".join(cards) + "</div>"


def project_url(row: pd.Series | dict[str, Any]) -> str:
    getter = row.get if hasattr(row, "get") else lambda key, default=None: default
    return safe_text(getter("repo_url") or getter("html_url"))


def project_display_rows(df: pd.DataFrame, top_n: int = 12, sort_by: str = "final_potential_score", ascending: bool = False) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    view = df.sort_values(sort_by, ascending=ascending).head(top_n).copy() if sort_by in df.columns else df.head(top_n).copy()
    rows: list[dict[str, Any]] = []
    for _, row in view.iterrows():
        rows.append(
            {
                "仓库名称": safe_text(row.get("full_name")),
                "链接": project_url(row),
                "项目主题": project_topic(row),
                "主要语言": safe_text(row.get("language"), "Unknown"),
                "Stars": int(row.get("stars_total", 0) or 0),
                "Forks": int(row.get("forks_total", 0) or 0),
                "推荐等级": display_level(row.get("recommendation_level")),
                "综合潜力分": round(float(row.get("final_potential_score", 0) or 0), 2),
                "个性化匹配分": round(float(row.get("personalized_score", row.get("base_score", 0)) or 0), 2),
                "风险分": round(float(row.get("risk_score", 0) or 0), 2),
                "项目类型": display_cluster(row.get("cluster_name")),
            }
        )
    return pd.DataFrame(rows)


def render_project_cards(
    df: pd.DataFrame,
    *,
    top_n: int = 12,
    sort_by: str = "final_potential_score",
    ascending: bool = False,
    show_rank: bool = True,
    personalized: bool = False,
) -> None:
    if df.empty:
        st.info("暂无可展示项目。")
        return
    view = df.sort_values(sort_by, ascending=ascending).head(top_n).copy() if sort_by in df.columns else df.head(top_n).copy()
    cards = []
    for idx, (_, row) in enumerate(view.iterrows(), start=1):
        repo = safe_text(row.get("full_name"))
        url = project_url(row)
        repo_html = f"<a href='{html.escape(url)}' target='_blank'>{html.escape(repo)}</a>" if url else html.escape(repo)
        score_label = "个性化匹配分" if personalized else "综合潜力分"
        score_col = "personalized_score" if personalized and "personalized_score" in row else "final_potential_score"
        risk = float(row.get("risk_score", 0) or 0)
        reason = safe_text(row.get("recommended_action") or row.get("match_reason") or "")
        reason_html = f"<p class='topic'>{html.escape(reason)}</p>" if reason else f"<p class='topic'>{html.escape(project_topic(row))}</p>"
        rank_html = badge(f"第 {idx} 名", "fog") if show_rank else ""
        cards.append(
            "<div class='project-card'>"
            f"<h4>{rank_html} {repo_html}</h4>"
            f"{reason_html}"
            f"<div>{badge(display_level(row.get('recommendation_level')))} {badge(display_cluster(row.get('cluster_name')), 'fog')}</div>"
            "<div class='project-meta'>"
            f"<span>语言：{html.escape(safe_text(row.get('language'), 'Unknown'))}</span>"
            f"<span>Stars：{int(row.get('stars_total', 0) or 0):,}</span>"
            f"<span>Forks：{int(row.get('forks_total', 0) or 0):,}</span>"
            f"<span>{score_label}：{float(row.get(score_col, 0) or 0):.2f}</span>"
            f"<span>风险分：{risk:.2f}</span>"
            f"<span>{badge('查看 GitHub') if url else badge('无链接', 'slate')}</span>"
            "</div>"
            "</div>"
        )
    st.markdown("<div class='project-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_project_table(df: pd.DataFrame, *, top_n: int = 20, sort_by: str = "final_potential_score", ascending: bool = False) -> None:
    view = project_display_rows(df, top_n=top_n, sort_by=sort_by, ascending=ascending)
    if view.empty:
        st.info("暂无可展示项目。")
        return
    html_rows = []
    for _, row in view.iterrows():
        repo = html.escape(safe_text(row["仓库名称"]))
        url = html.escape(safe_text(row["链接"]))
        repo_html = f"<a href='{url}' target='_blank'>{repo}</a>" if url else repo
        html_rows.append(
            "<tr>"
            f"<td style='min-width:180px'>{repo_html}</td>"
            f"<td style='min-width:120px'>{html.escape(safe_text(row['项目主题']))}</td>"
            f"<td>{html.escape(safe_text(row['主要语言']))}</td>"
            f"<td>{int(row['Stars']):,}</td>"
            f"<td>{int(row['Forks']):,}</td>"
            f"<td>{badge(row['推荐等级'])}</td>"
            f"<td>{float(row['综合潜力分']):.2f}</td>"
            f"<td>{float(row['风险分']):.2f}</td>"
            f"<td style='min-width:150px'>{badge(row['项目类型'], 'fog')}</td>"
            "</tr>"
        )
    table = (
        "<div class='wide-table'><table><thead><tr>"
        "<th>仓库名称</th><th>项目主题</th><th>主要语言</th><th>Stars</th><th>Forks</th>"
        "<th>推荐等级</th><th>综合潜力分</th><th>风险分</th><th>项目类型</th>"
        "</tr></thead><tbody>"
        + "".join(html_rows)
        + "</tbody></table></div>"
    )
    st.markdown(table, unsafe_allow_html=True)


def progress_bar(label: str, value: float, *, warning: bool = False) -> None:
    pct = max(0.0, min(100.0, float(value or 0)))
    css_class = "custom-progress warning" if warning else "custom-progress"
    st.markdown(
        f"<div class='progress-label'><span>{html.escape(label)}</span><span>{pct:.2f}</span></div>"
        f"<div class='{css_class}'><span style='width:{pct:.2f}%'></span></div>",
        unsafe_allow_html=True,
    )


def render_profile_summary(profile: Any) -> None:
    data = profile.to_dict() if hasattr(profile, "to_dict") else dict(profile or {})
    items = [
        ("目标", data.get("main_goal", "选择可复现项目")),
        ("编程水平", data.get("programming_level", "中等")),
        ("偏好语言", "、".join(data.get("preferred_languages", []) or ["Python"])),
        ("偏好主题", "、".join(data.get("preferred_topics", []) or ["Coding Agent"])),
        ("运行条件", display_hardware(data.get("hardware_condition"))),
        ("风险偏好", data.get("risk_preference", "平衡")),
        ("输出偏好", "、".join(data.get("output_preference", []) or ["排行榜"])),
    ]
    cards = [
        f"<div class='profile-card'>{badge(label, 'fog')}<p>{html.escape(safe_text(value))}</p></div>"
        for label, value in items
    ]
    st.markdown("<div class='project-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_agent_showcase(record: dict[str, Any]) -> None:
    title = safe_text(record.get("title"))
    title_cn = safe_text(record.get("title_cn") or AGENT_NAME_CN.get(title, title))
    role = safe_text(record.get("role_cn"), "将数据证据转写为可读解释。")
    summary = safe_text(record.get("summary"), "当前结论已结合项目数据、模型结果与报告图表进行整理。")
    findings = _items_to_text(record.get("key_findings") or record.get("evidence") or [], "当前判断需结合对应图表与项目记录理解。")
    recommendations = _items_to_text(record.get("next_steps") or record.get("recommendations") or [], "建议先核对项目文档，再完成最小复现实验。")
    risks = _items_to_text(record.get("risks") or record.get("weak_sentences") or [], "结论用于选题辅助，不代表项目未来表现。")
    evidence = _items_to_text(record.get("evidence") or record.get("key_findings") or [], "依据来自仓库信息、评分结果与模型产物。")
    st.markdown(
        "<div class='agent-showcase-card'>"
        f"<h4>{html.escape(title_cn)}</h4>"
        f"<p>{badge('智能体职责', 'fog')} {html.escape(role)}</p>"
        f"<p>{badge('核心判断')} {html.escape(summary)}</p>"
        "<div class='agent-section-grid'>"
        f"<div class='agent-section'><b>核心判断</b><p>{findings}</p></div>"
        f"<div class='agent-section'><b>建议动作</b><p>{recommendations}</p></div>"
        f"<div class='agent-section'><b>相关依据</b><p>{evidence}</p></div>"
        f"<div class='agent-section'><b>风险提醒</b><p>{risks}</p></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if record.get("codex_prompt"):
        st.markdown(f"<div class='code-box'>{html.escape(safe_text(record['codex_prompt']))}</div>", unsafe_allow_html=True)


def _items_to_text(items: Iterable[Any], fallback: str) -> str:
    values = []
    for item in list(items)[:4]:
        if isinstance(item, dict):
            text = item.get("finding") or item.get("action") or item.get("risk") or item.get("sentence") or item.get("evidence") or item.get("reason")
        else:
            text = item
        text = safe_text(text)
        if text:
            values.append(html.escape(text))
    return "<br>".join(values) if values else html.escape(fallback)


def clean_sentence(text: Any) -> str:
    value = safe_text(text)
    legacy_local = "CPU" + "-only"
    for token in ["[", "]", '"', "'", legacy_local, "CPU" + " only"]:
        value = value.replace(token, "")
    value = value.replace("硬件适配：", "运行条件匹配：")
    value = value.replace(f"{legacy_local} 用户", "本地普通电脑用户")
    return value.strip(" -，。") + ("。" if value and not value.endswith(("。", ".", "！", "!")) else "")
