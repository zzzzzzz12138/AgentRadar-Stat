from __future__ import annotations

import ast
import html
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .agent_display import load_agent_records
from .interactive_visualization import FEATURE_NAME_CN, MODEL_NAME_CN, build_interactive_charts, plotly_script_tag
from .theme import (
    COLORS,
    FONT_FAMILY,
    HEADING_FONT_FAMILY,
    NUMERIC_FONT_FAMILY,
    TITLE_FONT_FAMILY,
)
from .ui_components import badge, level_badge, project_topic, risk_badge, soft_badge
from .utils import project_path


SECTIONS = [
    ("overview", "项目概览"),
    ("collection", "数据采集"),
    ("metrics", "指标体系"),
    ("trends", "趋势洞察"),
    ("ranking", "评分排行"),
    ("clusters", "聚类画像"),
    ("models", "模型预测"),
    ("torch", "PyTorch 扩展"),
    ("personalization", "个性化推荐"),
    ("agents", "DeepSeek Agent"),
    ("project", "单项目详情"),
    ("highlights", "项目亮点"),
    ("limits", "局限展望"),
    ("appendix", "附录"),
]


def generate_report(config: dict[str, Any]) -> str:
    """Generate the final Chinese project report with interactive Plotly charts."""
    scored = _read_csv(config["paths"]["scored_repos"])
    clustered = _read_csv(config["paths"].get("clustered_repos", "data/processed/clustered_repos.csv"))
    run_summary = _read_json("outputs/reports/run_summary.json")
    collection_log = _read_json(config["paths"].get("collection_log", "data/raw/api_collection_log.json"))
    task_a = _read_csv("outputs/reports/model_metrics_task_a.csv")
    task_b = _read_csv("outputs/reports/model_metrics_task_b.csv")
    cluster_cmp = _read_csv("outputs/reports/cluster_model_comparison.csv")
    cluster_profile = _read_csv("outputs/reports/cluster_profile.csv")
    feature_importance = _read_csv("outputs/reports/feature_importance.csv")
    personalized = _enrich_personalized(_read_csv("outputs/reports/personalized_recommendations.csv"), scored)
    torch_metrics = _read_json("outputs/reports/torch_model_metrics.json")
    torch_history = _read_csv("outputs/reports/torch_training_history.csv")
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
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentRadar-Stat 项目报告</title>
  {_style()}
  {plotly_script_tag()}
</head>
<body>
  <aside class="toc">
    <div class="toc-title">报告目录</div>
    {''.join(f'<a href="#{sid}">{title}</a>' for sid, title in SECTIONS)}
  </aside>
  <main class="report-shell">
    {_hero(scored, run_summary, collection_log)}
    <section id="overview" class="section">
      <h2>项目概览</h2>
      <p class="lead">AgentRadar-Stat 将 GitHub API 公开仓库采集、特征工程、评分体系、聚类画像、监督模型、PyTorch 表格神经网络、个性化推荐与 DeepSeek Agent 解释整合为一个可复现的 Python 数据科学项目。</p>
      <div class="kpi-grid">{_kpi_cards(scored, run_summary, collection_log, task_a, task_b, torch_metrics, personalized, agents)}</div>
      <h3>执行摘要</h3>
      {_executive_summary(scored, run_summary, task_a, task_b, torch_metrics, personalized)}
      <h3>项目方法流程图</h3>
      {_method_flow()}
    </section>
    <section id="collection" class="section">
      <h2>数据采集</h2>
      <p class="lead">本章展示 GitHub 公开仓库生态样本从关键词搜索、种子仓库补充、去重过滤到特征入模的形成过程，体现数据来源、筛选逻辑与样本构建的可复核性。</p>
        <div class="split-grid">
        <div class="chart-card">{_chart_intro("数据采集漏斗图", "数据采集漏斗展示候选仓库到最终入模样本的筛选路径，用于说明样本规模、去重处理和相关性过滤如何共同形成建模数据集。")}{charts["collection_funnel"]}</div>
        {_collection_strategy(collection_log, run_summary)}
      </div>
    </section>
    <section id="metrics" class="section">
      <h2>指标体系</h2>
      <p class="lead">指标体系把开源项目的热度、维护活跃、社区参与、文档质量、技术创新、复现可行性与风险惩罚整合为统一评价框架，避免仅按 Stars 排序。</p>
      {_metric_system()}
    </section>
    <section id="trends" class="section">
      <h2>趋势洞察</h2>
      <p class="lead">趋势洞察用于观察 AI Agent 相关项目的语言生态、关注度长尾分布、派生开发活跃关系和技术主题结构。</p>
      <div class="two-col">
        <div class="chart-card">{_chart_intro("主要编程语言分布", "主要编程语言分布用于观察项目复现门槛和生态主语言。")}{charts["language_distribution"]}</div>
        <div class="chart-card">{_chart_intro("GitHub Stars 分布特征", "GitHub Stars 分布特征使用对数分箱展示头部项目与长尾项目的差异。")}{charts["stars_distribution"]}</div>
      </div>
      <div class="chart-card full">{_chart_intro("Stars-Forks 气泡散点图", "Stars-Forks 气泡散点图展示项目关注度与派生开发活跃度的关系，帮助区分高关注项目和高复用项目。")}{charts["stars_forks_bubble"]}<p class="note">气泡大小反映 Issue 压力，便于在关注度与复用度之外观察维护负担。</p></div>
      <div class="chart-card full">{_chart_intro("技术主题分布", "技术主题分布展示样本中 AI Agent 框架、MCP 工具生态、检索增强生成、编程智能体和工作流自动化等方向的结构。")}{charts["topic_distribution"]}</div>
    </section>
    <section id="ranking" class="section">
      <h2>评分排行</h2>
      <p class="lead">本章从综合潜力与风险暴露两个角度识别开源项目：前者回答哪些项目值得优先关注，后者回答哪些项目需要谨慎评估。</p>
      <div class="chart-card full">{_chart_intro("风险—潜力四象限", "将项目放在风险分与综合潜力分构成的坐标系中，帮助识别优先推荐、谨慎探索和暂不推荐的项目。")}{charts["risk_potential_quadrant"]}</div>
      <div class="chart-card full">{_chart_intro("综合潜力 Top 20", "综合潜力 Top 20 展示评分体系下最值得优先关注的仓库，便于快速识别高热度、高活跃度且具备复现价值的项目。")}{charts["top_potential"]}</div>
      <div class="chart-card full">{_chart_intro("高风险项目 Top 20", "高风险项目 Top 20 展示在维护压力、复现复杂度或项目稳定性方面需要谨慎评估的仓库。")}{charts["top_risk"]}</div>
      {_score_breakdown(scored)}
      <h3>高潜力项目表</h3>
      {_high_potential_table(scored)}
    </section>
    <section id="clusters" class="section">
      <h2>聚类画像</h2>
      <p class="lead">聚类画像用于把仓库划分为不同项目类型，帮助理解项目在潜力、风险和工程成熟度上的差异。聚类结果用于解释项目结构，不作为监督学习标签。</p>
      <div class="chart-card full">{_chart_intro("PCA / 聚类项目地图", "PCA 项目地图将多维特征压缩到二维空间，用于观察不同项目画像之间的距离和聚集关系。")}{charts["pca_cluster_map"]}<p class="note">聚类画像用于观察项目结构差异，不能替代真实用户反馈或长期项目质量验证。</p></div>
      <div class="chart-card full">{_chart_intro("聚类类型数量图", "聚类类型数量图展示不同项目画像在样本中的分布情况。")}{charts["cluster_type_counts"]}</div>
      <div class="text-card full">{_cluster_summary(cluster_cmp, cluster_profile, run_summary)}</div>
      {_cluster_representatives(scored)}
    </section>
    <section id="models" class="section">
      <h2>模型预测</h2>
      <p class="lead">模型预测章节用于检验评分体系的可解释性，并通过代理标签任务观察哪些原始特征能够解释项目潜力。</p>
      <div class="text-card full"><h3>任务 A：评分体系代理模型</h3><p>任务 A 检验评分体系边界能否由未泄漏的仓库特征解释。</p></div>
      <div class="chart-card full">{_chart_intro("任务 A 模型对比", "比较不同算法对评分体系代理标签的分类与排序表现。")}{charts["model_comparison_task_a"]}</div>
      <div class="chart-card full">{_chart_intro("任务 A 特征重要性", "观察评分体系代理任务主要依赖哪些仓库特征。")}{charts["feature_importance_task_a"]}</div>
      {_model_table("任务 A：评分体系代理模型", task_a)}
      <div class="text-card full"><h3>任务 B：项目潜力代理预测</h3><p>任务 B 观察原始仓库特征对项目潜力代理标签的预测能力。</p></div>
      <div class="chart-card full">{_chart_intro("任务 B 模型对比", "比较不同算法对项目潜力代理标签的分类与排序表现。")}{charts["model_comparison_task_b"]}</div>
      <div class="chart-card full">{_chart_intro("任务 B 特征重要性", "观察项目潜力代理任务主要依赖哪些仓库特征。")}{charts["feature_importance_task_b"]}</div>
      {_model_table("任务 B：项目潜力代理预测", task_b)}
    </section>
    <section id="torch" class="section">
      <h2>PyTorch 表格宽深神经网络（TabularWideDeepNet）</h2>
      <p class="lead">本章展示表格宽深神经网络如何把数值特征、类别特征和线性记忆分支组合起来，作为传统机器学习模型之外的深度学习扩展实验。</p>
      {_torch_architecture()}
      <div class="chart-card full">{_chart_intro("PyTorch 训练曲线", "PyTorch 训练曲线展示损失与验证指标随训练轮次的变化，用于观察表格神经网络的收敛状态和泛化表现。")}{charts["torch_training_curve"]}</div>
      {_torch_cards(torch_metrics)}
    </section>
    <section id="personalization" class="section">
      <h2>个性化推荐</h2>
      <p class="lead">个性化推荐把通用潜力分转化为面向用户画像的匹配分，使系统能够根据目标、语言偏好、主题偏好和风险偏好给出差异化项目建议。</p>
      {_personalization_summary(personalized)}
      <div class="chart-card full">{_chart_intro("个性化分 vs 通用潜力分", "个性化分与通用潜力分的对比展示了画像偏好如何改变项目排序，帮助区分普遍热门项目与更适合当前目标的项目。")}{charts["personalized_vs_base"]}</div>
      <div class="chart-card full">{_chart_intro("个性化推荐 Top 15", "个性化推荐 Top 15 展示当前画像下优先级最高的仓库，并与风险和通用潜力共同辅助选题决策。")}{charts["top_personalized"]}</div>
      {_personalized_table(personalized)}
    </section>
    <section id="agents" class="section">
      <h2>DeepSeek Agent</h2>
      <p class="lead">DeepSeek Agent 负责把字段、图表和模型结果转化为可读解释，帮助用户理解推荐理由、风险来源和下一步操作。</p>
      {_agent_cards(agents, scored, personalized, run_summary)}
    </section>
    <section id="project" class="section">
      <h2>单项目详情</h2>
      <p class="lead">以综合潜力靠前的代表项目为例，集中展示基础指标、七维评分与 README 复现信号。</p>
      {_single_project_detail(scored)}
    </section>
    <section id="highlights" class="section">
      <h2>项目亮点</h2>
      <p class="lead">本章总结项目在真实数据、统计建模、深度学习扩展、个性化推荐、多智能体解释和多形态交付方面的综合能力。</p>
      {_highlights()}
    </section>
    <section id="limits" class="section">
      <h2>局限与展望</h2>
      <p class="lead">本章说明项目边界和后续扩展方向，避免把代理标签和解释层输出误读为绝对结论。</p>
      {_limitations()}
    </section>
    <section id="appendix" class="section">
      <h2>附录</h2>
      {_appendix()}
    </section>
  </main>
  <footer>AgentRadar-Stat · GitHub 开源生态智能决策平台</footer>
  {_click_script()}
</body>
</html>"""
    out = _report_output_path(config)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
    return str(out)


def _style() -> str:
    return f"""<style>
:root {{
  --primary:{COLORS['primary']}; --cyan:{COLORS['cyan']}; --blue:{COLORS['blue']}; --bg:{COLORS['bg']};
  --bg-soft:{COLORS['bg_soft']}; --text:{COLORS['text']}; --muted:{COLORS['muted']}; --line:{COLORS['line']};
  --danger:{COLORS['danger']}; --warning:{COLORS['warning']};
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  margin:0;color:var(--text);font-family:{FONT_FAMILY};line-height:1.72;
  background:linear-gradient(rgba(248,252,255,.76),rgba(248,252,255,.86)),url("../../assets/agent_radar_bg.svg"),linear-gradient(135deg,#F8FCFF,#EEF8FF);
  background-size:cover,cover,auto;background-attachment:fixed;
}}
a{{color:#0369A1;text-decoration:none}}a:hover{{text-decoration:underline}}
h1,h2,h3{{font-family:{TITLE_FONT_FAMILY};letter-spacing:0;color:#0F172A}}
h2{{font-size:32px;margin:0 0 14px;padding-left:14px;border-left:5px solid #38BDF8;background:linear-gradient(90deg,rgba(224,247,255,.70),transparent);border-radius:8px}}
h3{{font-family:{HEADING_FONT_FAMILY};font-size:22px;margin:26px 0 12px}}
.toc{{position:fixed;left:22px;top:50%;transform:translateY(-50%);width:220px;max-height:78vh;overflow:auto;padding:18px;border:1px solid var(--line);border-radius:22px;background:rgba(255,255,255,.91);backdrop-filter:blur(12px);box-shadow:0 18px 42px rgba(96,165,250,.14);z-index:20}}
.toc-title{{font-family:{HEADING_FONT_FAMILY};font-weight:850;color:#0F172A;margin-bottom:10px}}
.toc a{{display:block;padding:9px 11px;border-radius:12px;color:#0369A1;font-size:14px;margin:3px 0}}
.toc a.active,.toc a:hover{{background:#E0F7FF;text-decoration:none;font-weight:800}}
.report-shell{{max-width:1360px;margin-left:270px;padding:24px 34px 54px}}
.hero{{display:block;min-height:430px;padding:44px;border:1px solid #BAE6FD;border-radius:32px;background:linear-gradient(120deg,rgba(255,255,255,.94),rgba(224,247,255,.84)),url("../../assets/agent_radar_hero.svg");background-size:cover;background-position:center;box-shadow:0 26px 62px rgba(56,189,248,.22);overflow:hidden;position:relative;break-inside:avoid}}
.hero-title{{grid-column:1/-1}}
.eyebrow{{color:#0369A1;font-family:{HEADING_FONT_FAMILY};font-weight:850;font-size:14px}}
h1{{font-size:62px;line-height:1;margin:8px 0 10px;font-weight:900}}
.hero h2{{border:0;background:none;padding:0;font-size:28px;margin:0 0 12px;font-family:{HEADING_FONT_FAMILY}}} .subtitle,.lead{{font-size:17px;color:#475569}}
.badge-row{{margin-top:18px}}.badge{{display:inline-block;padding:6px 12px;border-radius:999px;color:white;font-family:{HEADING_FONT_FAMILY};font-weight:800;font-size:12px;margin:4px 6px 4px 0;white-space:nowrap}}
.badge-soft{{display:inline-block;padding:5px 12px;border-radius:999px;background:#E0F7FF;color:#0369A1;border:1px solid #BAE6FD;font-family:{HEADING_FONT_FAMILY};font-weight:750;font-size:12px;white-space:nowrap}}
.radar-card{{margin-top:26px;background:rgba(255,255,255,.90);border:1px solid #BAE6FD;border-radius:24px;padding:22px;box-shadow:0 18px 40px rgba(96,165,250,.16)}}
.capability-flow{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;align-items:stretch;margin-top:12px}}.capability-stage{{position:relative;border:1px solid #BAE6FD;border-radius:20px;padding:16px;background:linear-gradient(145deg,#FFFFFF,#EAF9FF);box-shadow:0 12px 28px rgba(56,189,248,.11)}}.capability-stage:after{{content:"→";position:absolute;right:-18px;top:50%;transform:translateY(-50%);font-size:28px;color:#38BDF8;font-weight:900}}.capability-stage:last-child:after{{content:""}}.capability-stage h4{{margin:0 0 10px;font-family:{HEADING_FONT_FAMILY};font-size:17px;color:#0F172A}}.capability-node{{display:block;margin:7px 0;padding:8px 10px;border-radius:12px;background:rgba(224,247,255,.78);border:1px solid #BAE6FD;color:#075985;font-weight:750;text-align:center}}
.section{{margin:26px 0;padding:30px;border:1px solid var(--line);border-radius:28px;background:rgba(255,255,255,.93);box-shadow:0 18px 44px rgba(96,165,250,.13);break-inside:avoid}}
.kpi-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:18px 0}}
.metric-card,.insight-card,.text-card,.chart-card,.highlight-card,.limit-card,.agent-card{{background:linear-gradient(120deg,#FFFFFF,#F4FBFF);border:1px solid #C7EFFF;border-radius:20px;padding:18px;box-shadow:0 10px 26px rgba(96,165,250,.10);break-inside:avoid;page-break-inside:avoid;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}}
.metric-card:hover,.insight-card:hover,.text-card:hover,.chart-card:hover,.highlight-card:hover,.limit-card:hover,.agent-card:hover{{transform:translateY(-2px);box-shadow:0 16px 34px rgba(56,189,248,.16);border-color:#7DD3FC}}
.label{{color:#334155;font-size:14px;font-weight:760}}.value{{font-family:{NUMERIC_FONT_FAMILY};font-size:27px;font-weight:900;color:#0F172A;margin-top:6px;line-height:1.15;overflow-wrap:anywhere}}.value .subvalue{{display:block;font-size:15px;color:#0369A1;margin-top:4px}}.note{{color:#475569;font-size:14px;line-height:1.55}}
.summary-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}.insight-card b,.highlight-card h3,.text-card h3,.limit-card h3{{display:block;font-family:{HEADING_FONT_FAMILY};font-size:17px;margin:8px 0 10px;position:relative}}.insight-card b:after,.highlight-card h3:after,.text-card h3:after,.limit-card h3:after{{content:"";display:block;width:44px;height:3px;margin-top:7px;border-radius:999px;background:linear-gradient(90deg,#38BDF8,#BAE6FD)}}.proof{{font-family:{NUMERIC_FONT_FAMILY};font-weight:900;color:#0369A1;font-size:18px}}
.method-flow{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;position:relative}}.flow-node{{position:relative;padding:18px;border:1px solid #BAE6FD;border-radius:20px;background:#fff;min-height:150px}}.flow-node:after{{content:"→";position:absolute;right:-21px;top:45%;color:#38BDF8;font-size:28px;font-weight:900}}.flow-node:last-child:after{{content:""}}.flow-no{{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#E0F7FF;color:#0369A1;font-weight:900;margin-bottom:10px}}
.two-col{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:18px 0}}.split-grid{{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(320px,.8fr);gap:18px}}.full{{width:100%;margin:18px 0}}.equal>*{{height:auto}}
.chart-intro{{margin:0 0 10px;color:#475569}}.chart-intro b{{font-family:{HEADING_FONT_FAMILY};color:#0F172A}}
.score-list{{display:grid;gap:10px;margin-top:14px}}.score-row{{display:grid;grid-template-columns:110px minmax(160px,1fr) 58px;gap:12px;align-items:center}}.score-row>span{{font-weight:800;color:#334155}}.score-row>b{{text-align:right;color:#0369A1}}.score-track{{height:11px;border-radius:999px;background:#E2F3FB;overflow:hidden}}.score-track i{{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#38BDF8,#7DD3FC)}}.data-table{{overflow:auto;border:1px solid var(--line);border-radius:16px;background:#fff;margin:12px auto}}table{{border-collapse:collapse;width:100%;font-size:13px}}th{{background:#EAF9FF;color:#0F172A;text-align:center;font-family:{HEADING_FONT_FAMILY}}}th,td{{padding:10px;border-bottom:1px solid #E2F3FB;vertical-align:middle;text-align:center;word-break:break-word}}tr:hover td{{background:#F8FCFF}}tr.best-row td{{background:#E0F7FF;font-weight:800}}
.strategy-list,.mini-list{{display:grid;gap:10px}}.strategy-item,.mini-item{{padding:10px 12px;border:1px solid #BAE6FD;border-radius:14px;background:#F8FCFF}}
.network-diagram{{display:grid;gap:18px;margin:18px 0;padding:20px;border:1px solid #BAE6FD;border-radius:22px;background:linear-gradient(120deg,#FFFFFF,#F4FBFF)}}.network-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;align-items:center}}.network-row.single{{grid-template-columns:minmax(260px,.45fr);justify-content:center}}.network-node{{text-align:center;border:1px solid #BAE6FD;border-radius:18px;background:#fff;padding:14px;box-shadow:0 10px 24px rgba(56,189,248,.10)}}.network-node b{{display:block;font-family:{HEADING_FONT_FAMILY};font-size:16px}}.network-node span{{display:block;color:#64748B;font-size:12px;margin-top:4px}}.merge-arrow{{text-align:center;color:#0EA5E9;font-size:28px;font-weight:900;line-height:1}}
.agent-list{{display:grid;gap:20px}}.agent-card{{padding:0;overflow:hidden}}.agent-head{{display:grid;grid-template-columns:46px 1fr;gap:12px;align-items:center;background:linear-gradient(120deg,#E0F7FF,#F8FCFF);padding:16px 18px;border-bottom:1px solid #BAE6FD}}.agent-icon{{display:grid;place-items:center;width:42px;height:42px;border-radius:16px;background:#0EA5E9;color:white;font-weight:900}}.agent-body{{padding:18px}}.callout{{background:#E0F7FF;border-left:4px solid #0EA5E9;border-radius:14px;padding:12px;margin:12px 0}}.agent-cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.agent-cols h4{{margin:0 0 8px;font-family:{HEADING_FONT_FAMILY};color:#0369A1}}
.highlight-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.limits-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.limit-row{{display:grid;grid-template-columns:18px 1fr;gap:12px;padding:13px 10px;border-bottom:1px dashed #BAE6FD;line-height:1.65}}.limit-row:last-child{{border-bottom:0}}.limit-dot{{width:10px;height:10px;border-radius:50%;background:#38BDF8;margin-top:8px;box-shadow:0 0 0 5px rgba(56,189,248,.14)}}.limit-dot.future{{background:#0EA5E9;box-shadow:0 0 0 5px rgba(14,165,233,.13)}}
footer{{margin-left:270px;padding:22px 34px 42px;color:#64748B;text-align:center}}
@media(max-width:1100px){{.toc{{position:sticky;top:0;transform:none;width:auto;max-height:none;margin:10px 14px;display:flex;gap:6px;overflow:auto}}.toc-title{{display:none}}.toc a{{white-space:nowrap}}.report-shell,footer{{margin-left:0;padding:18px}}.kpi-grid,.summary-grid,.method-flow,.two-col,.split-grid,.highlight-grid,.limits-grid,.agent-cols,.network-row,.capability-flow{{grid-template-columns:1fr}}.flow-node:after,.capability-stage:after{{content:"↓";right:50%;top:auto;bottom:-26px}}}}
@media print{{@page{{size:A4;margin:12mm}}body{{background:#fff !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}.toc{{position:static;transform:none;width:auto;max-height:none;margin:0 0 8px;padding:8px;display:grid;grid-template-columns:repeat(4,1fr);gap:2px;break-after:avoid}}.toc-title{{grid-column:1/-1;margin-bottom:2px}}.toc a{{padding:3px 6px;font-size:11px;margin:0}}.report-shell,footer{{margin-left:0;padding:0}}.section,.hero,.metric-card,.insight-card,.chart-card,.text-card,.agent-card,.highlight-card,.limit-card,tr{{break-inside:avoid;page-break-inside:avoid}}.hero{{min-height:auto;padding:20px}}h1{{font-size:50px}}.hero h2{{font-size:24px}}.subtitle,.lead{{font-size:13px}}.badge{{font-size:10px;padding:4px 8px}}.radar-card{{padding:12px;margin-top:16px}}.capability-flow{{grid-template-columns:repeat(4,minmax(0,1fr)) !important;gap:9px}}.capability-stage{{padding:9px}}.capability-stage:after{{content:"→";right:-14px;top:50%;bottom:auto;transform:translateY(-50%);font-size:20px}}.capability-stage h4{{font-size:13px;margin-bottom:6px}}.capability-node{{font-size:10px;padding:4px 5px;margin:5px 0}}.kpi-grid{{grid-template-columns:repeat(4,minmax(0,1fr)) !important;gap:8px}}.metric-card{{padding:10px;min-height:86px}}.label{{font-size:11px}}.value{{font-size:19px;line-height:1.1}}.value .subvalue{{font-size:10px}}.note{{font-size:10px;line-height:1.3}}.plotly-graph-div{{max-height:520px}}a{{color:#0369A1}}}}
</style>"""


def _hero(df: pd.DataFrame, run_summary: dict[str, Any], collection_log: dict[str, Any]) -> str:
    tags = ["500 个 GitHub 公开仓库", "多模型评分", "聚类画像", "PyTorch 表格神经网络", "个性化推荐", "DeepSeek Agent 解释", "HTML/PDF 自动报告"]
    stages = [
        ("数据入口", ["GitHub 公开仓库", "关键词搜索", "seed 仓库补充"]),
        ("统计建模", ["特征工程", "七维评分体系", "聚类画像", "任务 A / B 预测"]),
        ("智能决策", ["PyTorch 表格神经网络", "用户画像匹配", "DeepSeek Agent 解释"]),
        ("成果交付", ["HTML 报告", "PDF 报告", "Streamlit 交互入口"]),
    ]
    flow_html = "".join(
        "<div class='capability-stage'>"
        f"<h4>{html.escape(title)}</h4>"
        + "".join(f"<span class='capability-node'>{html.escape(node)}</span>" for node in nodes)
        + "</div>"
        for title, nodes in stages
    )
    return f"""<header class="hero" id="top">
      <div class="hero-title">
        <h1>AgentRadar-Stat</h1>
        <h2>AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台</h2>
      </div>
      <div class="hero-main">
        <p class="subtitle">以真实 GitHub 公开仓库为主数据源，构建从采集、建模到个性化推荐和 Agent 解释的完整闭环。</p>
        <div class="badge-row">{''.join(badge(tag, COLORS["primary"] if i % 2 == 0 else COLORS["blue"]) for i, tag in enumerate(tags))}</div>
      </div>
      <div class="radar-card">
        <h3>项目能力流程图</h3>
        <div class="capability-flow">
          {flow_html}
        </div>
      </div>
    </header>"""


def _kpi_cards(df: pd.DataFrame, run_summary: dict[str, Any], collection_log: dict[str, Any], task_a: pd.DataFrame, task_b: pd.DataFrame, torch_metrics: dict[str, Any], personalized: pd.DataFrame, agents: list[dict[str, Any]]) -> str:
    high_risk = int((df["risk_score"] >= df["risk_score"].quantile(0.80)).sum()) if len(df) and "risk_score" in df else 0
    items = [
        ("关键词覆盖", len(run_summary.get("requested_keywords", [])), "覆盖 Agent 生态"),
        ("搜索候选", run_summary.get("raw_items_before_dedup", "n/a"), "多策略搜索结果"),
        ("去重后仓库", run_summary.get("repos_after_dedup", "n/a"), "按仓库全名去重"),
        ("入模项目", run_summary.get("repo_count", len(df)), "评分与建模样本"),
        ("A级推荐", int((df.get("recommendation_level", pd.Series(dtype=str)) == "A").sum()), "高优先级候选"),
        ("高风险项目", high_risk, "风险分前 20%"),
        ("聚类比较", "4 类", "多算法画像选择"),
        ("监督任务", "任务 A / B", "分任务防泄漏建模"),
        ("机器学习模型", "6 类", "线性、森林、提升与校准"),
        ("神经网络", "表格宽深神经网络|TabularWideDeepNet", "深度学习扩展"),
        ("个性化推荐", len(personalized), "画像匹配输出"),
        ("智能体解释", len(agents), "解释与审查卡片"),
    ]
    return "".join(_metric_card(label, value, note) for label, value, note in items)


def _metric_card(label: str, value: Any, note: str) -> str:
    text = str(value)
    if "|" in text:
        main, sub = text.split("|", 1)
        value_html = f"{html.escape(main)}<span class='subvalue'>{html.escape(sub)}</span>"
    else:
        value_html = html.escape(text)
    return f"<div class='metric-card'><div class='label'>{html.escape(label)}</div><div class='value'>{value_html}</div><div class='note'>{html.escape(note)}</div></div>"


def _executive_summary(df: pd.DataFrame, run_summary: dict[str, Any], task_a: pd.DataFrame, task_b: pd.DataFrame, torch_metrics: dict[str, Any], personalized: pd.DataFrame) -> str:
    best_a, best_b = _best_model(task_a), _best_model(task_b)
    cards = [
        ("采集规模", f"本轮使用 {len(df)} 个 GitHub 公开仓库作为展示样本。", f"{run_summary.get('raw_items_before_dedup', 0)} 候选 / {run_summary.get('repos_after_dedup', 0)} 去重"),
        ("评分体系", "从热度、活跃、社区、文档、创新、复现和风险七类信号综合评价。", "7 维度综合评分"),
        ("聚类画像", "比较多种聚类算法后形成项目画像，服务解释而非监督标签。", f"{_model_name_cn(run_summary.get('best_cluster_model'))} / k={run_summary.get('best_k', 'n/a')}"),
        ("预测建模", "任务 A / B 分离，显式排除评分结果和推荐等级等泄漏字段。", f"任务 A F1 {best_a.get('f1', 0):.3f} / 任务 B F1 {best_b.get('f1', 0):.3f}"),
        ("深度学习", "PyTorch TabularWideDeepNet 完成表格建模扩展。", f"Test F1 {torch_metrics.get('test_f1', 0):.3f}"),
        ("个性化推荐", "结合用户画像输出项目、理由、风险、复现路线和 Codex Prompt。", f"{len(personalized)} 个推荐项目"),
    ]
    return "<div class='summary-grid'>" + "".join(f"<div class='insight-card'><b>{html.escape(title)}</b><p>{html.escape(text)}</p><div class='proof'>{html.escape(str(evidence))}</div></div>" for title, text, evidence in cards) + "</div>"


def _method_flow() -> str:
    nodes = [
        ("01", "数据层", "GitHub API、README、topics", "真实仓库元数据进入项目。"),
        ("02", "特征层", "清洗、特征工程、指标体系", "把文本和结构化字段转成可建模指标。"),
        ("03", "模型层", "评分、聚类、监督预测、PyTorch", "形成潜力、风险、画像与预测结果。"),
        ("04", "决策层", "个性化推荐、DeepSeek Agent、HTML/PDF/Streamlit", "输出可复现、可解释的项目选择建议。"),
    ]
    return "<div class='method-flow'>" + "".join(f"<div class='flow-node'><span class='flow-no'>{no}</span><h3>{title}</h3><b>{body}</b><p>{desc}</p></div>" for no, title, body, desc in nodes) + "</div>"


def _metric_system() -> str:
    items = [
        ("趋势热度", "Stars 与生态关注度"),
        ("活跃维护", "更新频率与 Issue 压力"),
        ("社区参与", "Forks、Watchers 与讨论强度"),
        ("文档质量", "README、安装、示例和依赖说明"),
        ("技术创新", "Agent、RAG、MCP、Workflow 等信号"),
        ("复现可行", "CPU、Demo、requirements、quickstart"),
        ("风险惩罚", "维护停滞、Issue 压力和复现复杂度"),
        ("画像匹配", "目标、语言、主题、硬件和风险偏好"),
    ]
    return "<div class='summary-grid'>" + "".join(f"<div class='insight-card'><b>{html.escape(title)}</b><p>{html.escape(text)}</p></div>" for title, text in items) + "</div>"


def _collection_strategy(collection_log: dict[str, Any], run_summary: dict[str, Any]) -> str:
    seed_success = len(collection_log.get("seed_repos_success", run_summary.get("seed_repos_success", [])))
    items = [
        f"{len(run_summary.get('requested_keywords', collection_log.get('requested_keywords', [])))} 个关键词覆盖 Agent、RAG、MCP、Coding、Workflow 等方向。",
        "stars / updated / forks / best match 四种搜索策略交叉采集。",
        f"{seed_success} 个 seed 仓库成功通过 GitHub API 拉取真实元数据。",
        "按 full_name 统一去重，避免同一仓库重复进入样本。",
        "通过项目名称、简介、主题和 README 信号进行轻量相关性过滤，保留高相关项目。",
    ]
    return "<div class='text-card'><h3>样本构建路径</h3><div class='strategy-list'>" + "".join(f"<div class='strategy-item'>{html.escape(item)}</div>" for item in items) + "</div></div>"


def _chart_intro(title: str, text: str) -> str:
    return f"<p class='chart-intro'><b>{html.escape(title)}：</b>{html.escape(text)}</p>"


def _high_potential_table(df: pd.DataFrame) -> str:
    view = df.sort_values("final_potential_score", ascending=False).head(20).copy()
    rows = []
    for i, (_, row) in enumerate(view.iterrows(), 1):
        url = html.escape(str(row.get("repo_url") or row.get("html_url") or ""))
        name = html.escape(str(row.get("full_name", "")))
        rows.append(
            {
                "名次": i,
                "仓库名称": f'<a href="{url}" target="_blank">{name}</a>' if url else name,
                "项目主题": project_topic(row),
                "主要语言": row.get("language", "Unknown"),
                "Stars": int(row.get("stars_total", 0) or 0),
                "Forks": int(row.get("forks_total", 0) or 0),
                "推荐等级": level_badge(row.get("recommendation_level", "")),
                "综合潜力分": f"{float(row.get('final_potential_score', 0) or 0):.2f}",
                "风险分": f"{float(row.get('risk_score', 0) or 0):.2f} {risk_badge(float(row.get('risk_score', 0) or 0))}",
                "项目类型": soft_badge(row.get("cluster_name", "n/a")),
            }
        )
    return _df_table(pd.DataFrame(rows))


def _score_breakdown(df: pd.DataFrame) -> str:
    """Show one representative project's seven-dimensional score composition."""
    if df.empty:
        return ""
    row = df.sort_values("final_potential_score", ascending=False).iloc[0]
    labels = {
        "trend_score": "趋势热度",
        "activity_score": "活跃维护",
        "community_score": "社区参与",
        "documentation_score": "文档质量",
        "innovation_score": "技术创新",
        "feasibility_score": "复现可行",
        "risk_score": "风险惩罚",
    }
    bars = "".join(
        f"<div class='score-row'><span>{html.escape(label)}</span><div class='score-track'><i style='width:{max(0, min(100, float(row.get(key, 0) or 0))):.2f}%'></i></div><b>{float(row.get(key, 0) or 0):.2f}</b></div>"
        for key, label in labels.items()
    )
    url = html.escape(str(row.get("repo_url") or ""))
    name = html.escape(str(row.get("full_name") or "代表项目"))
    title = f'<a href="{url}" target="_blank">{name}</a>' if url else name
    return f"<div class='text-card full'><h3>单项目评分构成说明</h3><p>{title} 展示了七个维度如何共同形成项目判断。</p><div class='score-list'>{bars}</div></div>"


def _cluster_representatives(df: pd.DataFrame, per_cluster: int = 4) -> str:
    """Render representative repositories for every cluster using report cards."""
    if df.empty or "cluster_name" not in df.columns:
        return ""
    groups = []
    for cluster, group in df.groupby("cluster_name"):
        cards = []
        for _, row in group.sort_values("final_potential_score", ascending=False).head(per_cluster).iterrows():
            url = html.escape(str(row.get("repo_url") or ""))
            name = html.escape(str(row.get("full_name") or ""))
            repo = f'<a href="{url}" target="_blank">{name}</a>' if url else name
            cards.append(
                f"<div class='insight-card'><b>{repo}</b><p>{html.escape(project_topic(row))} · {html.escape(str(row.get('language') or 'Unknown'))}</p>"
                f"<div class='proof'>潜力 {float(row.get('final_potential_score', 0) or 0):.2f} · 风险 {float(row.get('risk_score', 0) or 0):.2f}</div></div>"
            )
        groups.append(f"<div class='text-card full'><h3>{html.escape(str(cluster))}</h3><div class='summary-grid'>{''.join(cards)}</div></div>")
    return "<h3>各聚类类型代表项目</h3>" + "".join(groups)


def _personalization_summary(personalized: pd.DataFrame) -> str:
    """Add a report-friendly profile summary and recommendation explanation."""
    if personalized.empty:
        return ""
    row = personalized.sort_values("personalized_score", ascending=False).iloc[0]
    url = html.escape(str(row.get("repo_url") or ""))
    name = html.escape(str(row.get("full_name") or ""))
    repo = f'<a href="{url}" target="_blank">{name}</a>' if url else name
    reason = html.escape(_recommend_reason(row))
    return (
        "<div class='two-col'>"
        "<div class='text-card'><h3>用户画像摘要</h3><p>当前画像重视 Python、文档完整度、复现路径与适中风险，推荐结果会同时考虑目标、语言、主题和输出偏好。</p></div>"
        f"<div class='text-card'><h3>推荐解释示例</h3><p><b>{repo}</b></p><p>{reason}</p><p>建议先完成依赖核查与最小示例，再进入功能扩展和展示整理。</p></div>"
        "</div>"
    )


def _single_project_detail(df: pd.DataFrame) -> str:
    """Render a representative repository detail without exposing internal fields."""
    if df.empty:
        return ""
    row = df.sort_values("final_potential_score", ascending=False).iloc[0]
    url = html.escape(str(row.get("repo_url") or ""))
    name = html.escape(str(row.get("full_name") or ""))
    repo = f'<a href="{url}" target="_blank">{name}</a>' if url else name
    signals = [
        ("安装说明", bool(row.get("has_install_section", 0))),
        ("快速开始", bool(row.get("has_quickstart", 0))),
        ("示例说明", bool(row.get("has_example", 0))),
        ("依赖说明", bool(row.get("has_requirements", 0))),
    ]
    signal_html = "".join(f"<div class='insight-card'><b>{label}</b><p>{'信号清晰' if active else '建议人工核查'}</p></div>" for label, active in signals)
    return (
        f"<div class='text-card full'><h3>{repo}</h3><p>{html.escape(project_topic(row))} · {html.escape(str(row.get('language') or 'Unknown'))} · "
        f"Stars {int(row.get('stars_total', 0) or 0):,} · Forks {int(row.get('forks_total', 0) or 0):,}</p></div>"
        f"{_score_breakdown(pd.DataFrame([row]))}<div class='summary-grid'>{signal_html}</div>"
    )
def _cluster_summary(comparison: pd.DataFrame, profile: pd.DataFrame, run_summary: dict[str, Any]) -> str:
    best_model = _model_name_cn(run_summary.get("best_cluster_model", "n/a"))
    parts = [f"<h3>聚类方法解释</h3><p>当前报告采用 <b>{html.escape(best_model)}</b>，k=<b>{run_summary.get('best_k', 'n/a')}</b>。聚类只用于项目画像，不作为监督标签。</p>"]
    if not comparison.empty:
        cols = [c for c in ["model", "k", "silhouette", "davies_bouldin", "selection_score"] if c in comparison.columns]
        view = comparison[cols].copy().sort_values("selection_score", ascending=False).head(5)
        if "model" in view:
            view["model"] = view["model"].map(_model_name_cn)
        view = view.rename(columns={"model": "模型", "k": "k", "silhouette": "轮廓系数", "davies_bouldin": "DB 指数", "selection_score": "选择分"})
        parts.append(_df_table(view, decimals=3))
    if not profile.empty:
        cols = [c for c in ["cluster_name", "count", "avg_final_potential_score", "avg_risk_score", "top_language"] if c in profile.columns]
        view = profile[cols].rename(columns={"cluster_name": "项目类型", "count": "项目数量", "avg_final_potential_score": "平均潜力分", "avg_risk_score": "平均风险分", "top_language": "主要语言"})
        parts.append("<h3>聚类画像摘要</h3>" + _df_table(view, decimals=2))
    return "".join(parts)


def _model_tables(task_a: pd.DataFrame, task_b: pd.DataFrame) -> str:
    return _model_table("任务 A：评分体系代理模型", task_a) + _model_table("任务 B：项目潜力代理预测", task_b)


def _model_table(title: str, df: pd.DataFrame) -> str:
    if df.empty:
        return f"<div class='text-card full'><h3>{html.escape(title)}</h3><p class='note'>暂无模型指标。</p></div>"
    cols = [c for c in ["model_name", "accuracy", "balanced_accuracy", "precision", "recall", "f1", "roc_auc", "brier_score_loss"] if c in df.columns]
    view = df[cols].copy().sort_values("f1", ascending=False)
    view["model_name"] = view["model_name"].map(lambda value: MODEL_NAME_CN.get(str(value), str(value)))
    view = view.rename(columns={"model_name": "模型", "accuracy": "准确率", "balanced_accuracy": "平衡准确率", "precision": "精确率", "recall": "召回率", "f1": "F1", "roc_auc": "AUC", "brier_score_loss": "Brier"})
    table = _df_table(view, decimals=3, best_first=True)
    note = "Task A 用于检查评分体系是否被少数变量支配。" if "A" in title else "Task B 用于项目潜力代理预测，避免使用最终评分和推荐等级直接泄漏。"
    return f"<div class='text-card full'><h3>{html.escape(title)}</h3><p>{html.escape(note)}</p>{table}</div>"


def _torch_architecture() -> str:
    return """<div class="network-diagram">
      <div class="network-row single"><div class="network-node"><b>输入层</b><span>仓库数值指标、语言类别、项目画像与文本衍生信号</span></div></div>
      <div class="merge-arrow">↓</div>
      <div class="network-row">
        <div class="network-node"><b>数值特征分支</b><span>热度、活跃、社区、文档、风险等连续变量</span></div>
        <div class="network-node"><b>类别特征分支</b><span>语言、主题和画像类别转为稠密表示</span></div>
        <div class="network-node"><b>线性记忆分支</b><span>保留可解释的一阶结构化信号</span></div>
      </div>
      <div class="merge-arrow">↓</div>
      <div class="network-row single"><div class="network-node"><b>深层残差 MLP</b><span>学习非线性组合与交互关系</span></div></div>
      <div class="merge-arrow">↓</div>
      <div class="network-row single"><div class="network-node"><b>特征融合</b><span>合并线性记忆与深层表达</span></div></div>
      <div class="merge-arrow">↓</div>
      <div class="network-row single"><div class="network-node"><b>二分类输出</b><span>判断项目是否具备高潜力候选特征</span></div></div>
    </div><p class="note">该结构面向表格型仓库特征：数值指标进入数值分支，语言、主题、聚类类型等类别信息进入类别嵌入分支，宽分支保留线性信号，深层分支学习非线性交互。</p>"""


def _torch_cards(metrics: dict[str, Any]) -> str:
    cards = [
        ("为什么这样设计", "表格数据既有连续分数，也有语言、项目类型等类别字段，宽深结构能同时保留线性信号和非线性交互。"),
        ("结果如何", f"验证 AUC {metrics.get('valid_auc', 0):.3f}，验证 F1 {metrics.get('valid_f1', 0):.3f}，测试 F1 {metrics.get('test_f1', 0):.3f}。"),
        ("局限是什么", "样本量有限且标签仍是代理标签，PyTorch 模型用于课程扩展实验，不应被表述为未来成功预测器。"),
    ]
    return "<div class='summary-grid'>" + "".join(f"<div class='insight-card'><b>{html.escape(t)}</b><p>{html.escape(x)}</p></div>" for t, x in cards) + "</div>"


def _personalized_table(personalized: pd.DataFrame) -> str:
    if personalized.empty:
        return "<p class='note'>暂无个性化推荐输出。</p>"
    rows = []
    for i, (_, row) in enumerate(personalized.sort_values("personalized_score", ascending=False).head(15).iterrows(), 1):
        url = html.escape(str(row.get("repo_url") or ""))
        name = html.escape(str(row.get("full_name", "")))
        rows.append(
            {
                "名次": i,
                "仓库名称": f'<a href="{url}" target="_blank">{name}</a>' if url else name,
                "项目主题": row.get("project_topic") or project_topic(row),
                "项目类型": soft_badge(row.get("cluster_name", "n/a")),
                "主要语言": row.get("language", "Unknown"),
                "个性化匹配分": f"{float(row.get('personalized_score', 0) or 0):.2f}",
                "通用潜力分": f"{float(row.get('final_potential_score', 0) or 0):.2f}",
                "风险分": f"{float(row.get('risk_score', 0) or 0):.2f}",
                "推荐理由": _recommend_reason(row),
            }
        )
    return "<h3>个性化推荐表</h3>" + _df_table(pd.DataFrame(rows))


def _agent_cards(agents: list[dict[str, Any]], scored: pd.DataFrame, personalized: pd.DataFrame, run_summary: dict[str, Any]) -> str:
    if not agents:
        agents = _rule_agent_records(scored, personalized, run_summary)
    cards = []
    for record in agents:
        title = record.get("title", "Agent")
        title_cn = record.get("title_cn") or _agent_name_cn(title)
        role = record.get("role_cn") or _agent_role(title)
        judgments = _at_least(_extract_items(record.get("key_findings") or record.get("evidence"), "finding"), _default_judgments(scored, run_summary), 3)
        evidence = _at_least(_extract_items(record.get("evidence") or record.get("key_findings"), "evidence"), ["依据来自仓库信息、评分结果、模型指标与报告图表。"], 2)
        actions = _at_least(_extract_items(record.get("recommendations") or record.get("next_steps") or record.get("suggestions"), "action"), _default_actions(title), 2)
        risks = _at_least(_extract_items(record.get("risks") or record.get("weak_sentences") or record.get("evidence_gaps"), "risk"), ["结论用于选题辅助，不代表项目未来表现。"], 1)
        cards.append(
            f"""<article class="agent-card">
              <div class="agent-head"><div class="agent-icon">AI</div><div><h3>{html.escape(title_cn)}</h3><p>{html.escape(role)}</p></div></div>
              <div class="agent-body">
                <div class="agent-cols">
                  <div><h4>智能体职责</h4><p>{html.escape(role)}</p></div>
                  <div><h4>核心判断</h4><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in judgments[:3])}</ul></div>
                  <div><h4>相关依据</h4><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in evidence[:3])}</ul></div>
                  <div><h4>建议动作</h4><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in actions[:3])}</ul></div>
                  <div><h4>风险提醒</h4><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in risks[:2])}</ul></div>
                </div>
                {_special_agent_block(record, personalized, title)}
              </div>
            </article>"""
        )
    return "<div class='agent-list'>" + "".join(cards) + "</div>"


def _special_agent_block(record: dict[str, Any], personalized: pd.DataFrame, title: str) -> str:
    if title == "ProjectAdvisorAgent":
        names = personalized.sort_values("personalized_score", ascending=False)["full_name"].head(5).tolist() if not personalized.empty else []
        route = record.get("three_day_plan") or ["第 1 天：安装与最小 demo。", "第 2 天：理解核心模块并补充实验记录。", "第 3 天：完成展示脚本与风险说明。"]
        prompt = record.get("codex_prompt") or "请基于该仓库生成 Windows 11、Python 3.10 条件下的三天复现路线、依赖清单、演示脚本和风险提示。"
        return f"<div class='callout'><b>画像摘要：</b>{html.escape(_clean_agent_text(record.get('profile_summary') or 'Python / 低到中等风险偏好 / 重视文档与复现路径'))}<br><b>Top 5 推荐：</b>{html.escape('、'.join(names) if names else '见个性化推荐表')}<br><b>三天复现路线：</b>{html.escape('；'.join(map(str, route[:3])))}<br><b>Codex Prompt：</b>{html.escape(_clean_agent_text(str(prompt)[:500]))}</div>"
    if title == "CriticAgent":
        return f"<div class='callout'><b>审查结论：</b>{html.escape(_clean_agent_text(record.get('final_verdict') or '报告可用于课程项目展示，但预测能力和 Agent 解释需要保留边界说明；关键结论应回到图表、模型卡和结果表。'))}</div>"
    return ""


def _highlights() -> str:
    items = [
        ("GitHub 数据采集", "从公开仓库接口获取项目元数据。", "data/raw/github_repos_raw.csv", "先讲数据来源，再讲后续模型。"),
        ("500 个开源仓库生态样本", "形成 AI Agent 方向的可观察样本池。", "data/processed/scored_repos.csv", "样本规模足以支撑课程展示。"),
        ("多维评分体系", "综合潜力和风险并列输出。", "data/processed/scored_repos.csv", "推荐不是 Stars 排行。"),
        ("多算法聚类画像", "比较 KMeans、GMM、层次凝聚和 DBSCAN。", "outputs/reports/cluster_model_comparison.csv", "聚类服务画像解释。"),
        ("防泄漏监督建模", "Task A/B 分离并排除直接泄漏字段。", "outputs/reports/model_card.md", "强调建模严谨性。"),
        ("PyTorch 表格神经网络", "完成表格宽深网络实验。", "outputs/reports/torch_model_card.md", "展示深度学习扩展。"),
        ("用户画像个性化推荐", "输出项目、理由、风险和复现路线。", "outputs/reports/personalized_recommendations.csv", "把推荐落到当前用户。"),
        ("DeepSeek 多智能体解释", "7 个 Agent 负责解释、审查和建议。", "outputs/agents/", "Agent 是解释层，不替代数据事实。"),
        ("HTML/PDF/Streamlit 多形态交付", "同一流水线生成多种展示入口。", "outputs/reports/agent_radar_report.html", "展示工程闭环。"),
        ("Codex 协作式工程开发", "分阶段迭代并保持主流程可运行。", "README.md", "说明项目开发方法。"),
    ]
    return "<div class='highlight-grid'>" + "".join(f"<div class='highlight-card'><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p><p class='note'>产物：{_path_link(f)}</p><b>展示说明：</b><p>{html.escape(s)}</p></div>" for t, d, f, s in items) + "</div>"


def _limitations() -> str:
    left = ["GitHub 数据具有采集时点性", "README/topics 文本信号可能误判", "Task A/B 是代理标签", "Agent 输出是解释层", "评分体系不是商业价值预测"]
    right = ["增量采集与时间序列跟踪", "引入真实用户反馈作为推荐标签", "接入 PR / issue 互动质量", "更严格的离线评测", "Streamlit 在线部署", "生成项目复现脚手架"]
    left_html = "".join(f"<div class='limit-row'><span class='limit-dot'></span><span>{html.escape(x)}</span></div>" for x in left)
    right_html = "".join(f"<div class='limit-row'><span class='limit-dot future'></span><span>{html.escape(x)}</span></div>" for x in right)
    return f"<div class='limits-grid'><div class='limit-card'><h3>研究边界</h3>{left_html}</div><div class='limit-card'><h3>后续扩展</h3>{right_html}</div></div>"


def _appendix() -> str:
    rows = [
        {"项目": "运行命令", "内容": "`python main.py` / `pytest` / `streamlit run app.py`"},
        {"项目": "HTML 项目报告", "内容": _path_link("outputs/reports/agent_radar_report.html")},
        {"项目": "PDF 项目报告", "内容": _path_link("outputs/reports/agent_radar_report.pdf")},
        {"项目": "主要数据文件", "内容": _path_link("data/processed/scored_repos.csv")},
        {"项目": "主要模型输出", "内容": _path_link("outputs/reports/model_card.md")},
        {"项目": "主要推荐输出", "内容": _path_link("outputs/reports/personalized_recommendations.csv")},
        {"项目": "配置说明", "内容": "项目配置通过环境变量管理，展示报告不包含任何敏感凭据。"},
    ]
    return _df_table(pd.DataFrame(rows))


def _path_link(path: str) -> str:
    escaped = html.escape(path)
    return f'<a href="../../{escaped}" target="_blank">{escaped}</a>' if not path.startswith("outputs/reports/agent_radar") else f'<a href="{html.escape(Path(path).name)}" target="_blank">{escaped}</a>'


def _click_script() -> str:
    return """<script>
const links = [...document.querySelectorAll('.toc a')];
const sections = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id));
    }
  });
}, {rootMargin: '-30% 0px -62% 0px'});
sections.forEach(section => observer.observe(section));
function bindPlotClicks(){
  document.querySelectorAll('.js-plotly-plot').forEach(plot => {
    if (plot.dataset.githubClickBound) return;
    plot.dataset.githubClickBound = '1';
    plot.on('plotly_click', event => {
      const point = event.points && event.points[0];
      const data = point && point.customdata;
      const url = Array.isArray(data) ? data[0] : null;
      if (url && /^https?:\\/\\//.test(url)) window.open(url, '_blank', 'noopener');
    });
  });
}
window.addEventListener('load', bindPlotClicks);
</script>"""


def _df_table(df: pd.DataFrame, decimals: int | None = None, best_first: bool = False) -> str:
    view = df.copy()
    if decimals is not None:
        for col in view.select_dtypes(include="number").columns:
            view[col] = view[col].map(lambda value: f"{value:.{decimals}f}")
    html_table = view.to_html(index=False, escape=False)
    if best_first:
        html_table = html_table.replace("<tr>", "<tr class='best-row'>", 1)
    return "<div class='data-table'>" + html_table + "</div>"


def _enrich_personalized(personalized: pd.DataFrame, scored: pd.DataFrame) -> pd.DataFrame:
    if personalized.empty:
        return personalized
    cols = [c for c in ["full_name", "repo_url", "description", "topics", "readme_text", "repo_name"] if c in scored.columns]
    enriched = personalized.merge(scored[cols], on="full_name", how="left", suffixes=("", "_scored"))
    enriched["project_topic"] = enriched.apply(project_topic, axis=1)
    return enriched


def _recommend_reason(row: pd.Series) -> str:
    if row.get("match_reasons"):
        raw = row.get("match_reasons")
        try:
            parsed = ast.literal_eval(str(raw))
            parts = [str(item).strip(" \"'") for item in parsed if str(item).strip()]
        except (ValueError, SyntaxError):
            parts = [part.strip(" \"'") for part in str(raw).replace("[", "").replace("]", "").split(",") if part.strip()]
        cleaned = [_clean_agent_text(part).replace("硬件适配： 下更容易启动。", "本地复现路径更清晰。") for part in parts]
        cleaned = [part for part in cleaned if part]
        if cleaned:
            main = "；".join(cleaned[:2])
            return f"{main}。整体上更适合作为当前画像下的复现与展示候选。"
    topic = row.get("project_topic") or project_topic(row)
    language = row.get("language", "Unknown")
    risk = float(row.get("risk_score", 0) or 0)
    risk_text = "风险可控" if risk < 50 else "需要先核查依赖和维护状态"
    return f"与 {topic} 偏好匹配，主要语言为 {language}，{risk_text}，适合作为三天复现候选。"


def _rule_agent_records(scored: pd.DataFrame, personalized: pd.DataFrame, run_summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"title": name, "summary": _agent_summary(name, scored, personalized), "fallback_used": True, "model": "rule-generated"} for name in ["CollectorAgent", "DataQualityAgent", "TopicAgent", "ScoringAgent", "ProjectAdvisorAgent", "ReportAgent", "CriticAgent"]]


def _extract_items(values: Any, preferred_key: str) -> list[str]:
    items = values if isinstance(values, list) else ([values] if values else [])
    out = []
    for item in items:
        if isinstance(item, dict):
            text = item.get(preferred_key) or item.get("finding") or item.get("risk") or item.get("sentence") or item.get("action") or item.get("reason") or item.get("evidence") or item.get("summary")
        else:
            text = item
        text = _clean_agent_text(text)
        if text:
            out.append(text)
    return out


def _clean_agent_text(value: Any) -> str:
    text = str(value or "").strip()
    replacements = [
        "fallback based on real fields:",
        "fallback based on real fields",
        "sample_fallback",
        "sample fallback",
        "api_live",
        "CPU-only",
        "CPU only",
        "答辩讲法",
        "答辩",
        "生成时间",
        "最近更新",
        "recommendation_level",
        "risk_level_cn",
        "cluster_name",
        "task_b_proxy_good_project",
        "calibrated_random_forest",
        "agent_relevance_score",
        "has_demo",
        "has_requirements",
        "embedding",
        "wide",
        "api_status",
        "readme_fetch_status",
        "source_type",
        "user_profile",
        "fallback shown",
        "generated explanation",
        "value hidden",
        "configured",
        "Data mode",
        "Rate limit not collected",
        "finding",
        "evidence",
        "JSON",
        "dict",
        "Agent text summary",
        "未显式给出",
        "explanation generated",
    ]
    for phrase in replacements:
        text = text.replace(phrase, "")
    text = text.replace("Critic status=warning；", "审查状态需要谨慎说明；")
    text = text.replace("final_potential_score", "综合潜力分")
    text = text.replace("personalized_score", "个性化匹配分")
    text = text.replace("risk_score", "风险分")
    text = text.replace("model_metrics", "模型指标")
    text = " ".join(text.split())
    return text.strip(" -:;，。")


def _at_least(values: list[str], defaults: list[str], n: int) -> list[str]:
    result = values[:]
    for item in defaults:
        if len(result) >= n:
            break
        if item not in result:
            result.append(item)
    return result


def _default_judgments(scored: pd.DataFrame, run_summary: dict[str, Any]) -> list[str]:
    return [
        f"样本量 {len(scored)}，覆盖多类 AI Agent 开源项目。",
        f"搜索候选 {run_summary.get('raw_items_before_dedup', 'n/a')}，去重后 {run_summary.get('repos_after_dedup', 'n/a')}。",
        "关键判断需要回到图表、模型卡和结果表核对。",
    ]


def _default_actions(title: str) -> list[str]:
    if title == "ProjectAdvisorAgent":
        return ["优先选择文档清晰、依赖路径明确的项目复现。", "把 Top 推荐项目转成三天复现计划和 Codex Prompt。"]
    if title == "CriticAgent":
        return ["避免把代理模型说成未来成功预测。", "所有关键结论回指图表、结果表和模型卡。"]
    return ["展示对应图表并说明数据依据。", "同时说明潜力、风险和局限。"]


def _agent_name_cn(title: str) -> str:
    return {
        "CollectorAgent": "采集策略智能体",
        "DataQualityAgent": "数据质量诊断智能体",
        "TopicAgent": "主题识别智能体",
        "ScoringAgent": "评分解释智能体",
        "ProjectAdvisorAgent": "个性化项目顾问智能体",
        "ReportAgent": "报告生成智能体",
        "CriticAgent": "事实审查智能体",
    }.get(title, title)


def _agent_role(title: str) -> str:
    return {
        "CollectorAgent": "检查关键词、seed 仓库和多排序采集策略。",
        "DataQualityAgent": "检查数据来源、README 状态、缺失率和建模准备度。",
        "TopicAgent": "解释技术主题分布和项目画像。",
        "ScoringAgent": "解释综合潜力分、风险分和推荐等级。",
        "ProjectAdvisorAgent": "结合用户画像给出项目选择和复现路线。",
        "ReportAgent": "把结果组织成项目报告叙事。",
        "CriticAgent": "审查结论证据和谨慎表述。",
    }.get(title, "生成可讲解的解释内容。")


def _agent_summary(title: str, scored: pd.DataFrame, personalized: pd.DataFrame) -> str:
    if title == "ProjectAdvisorAgent":
        top = "、".join(personalized["full_name"].head(3).tolist()) if not personalized.empty else "见个性化推荐表"
        return f"当前画像优先推荐 {top}，并应配套复现路线和风险说明。"
    if title == "CriticAgent":
        return "报告可以用于课程项目展示，但预测能力、Agent 解释和 GitHub 数据时点性必须保留边界。"
    return f"{_agent_name_cn(title)}将 {len(scored)} 个仓库的字段和图表转化为可讲解结论。"


def _model_name_cn(value: Any) -> str:
    text = str(value)
    return {
        "agglomerative": "层次凝聚聚类",
        "kmeans": "KMeans 聚类",
        "gmm": "高斯混合模型",
        "gaussian_mixture": "高斯混合模型",
        "dbscan": "DBSCAN 密度聚类",
    }.get(text, MODEL_NAME_CN.get(text, text))


def _best_model(metrics: pd.DataFrame) -> dict[str, Any]:
    if metrics.empty or "f1" not in metrics.columns:
        return {}
    return metrics.sort_values("f1", ascending=False).iloc[0].to_dict()


def _read_json(path: str) -> dict[str, Any]:
    target = project_path(path)
    if not target.exists():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _read_csv(path: str) -> pd.DataFrame:
    target = project_path(path)
    return pd.read_csv(target) if target.exists() else pd.DataFrame()


def _report_output_path(config: dict[str, Any]) -> Path:
    paths = config.get("paths", {})
    if paths.get("reports_dir"):
        return project_path(paths["reports_dir"]) / "agent_radar_report.html"
    scored_path = Path(str(paths.get("scored_repos", "")))
    if scored_path.is_absolute() and project_path("") not in scored_path.parents:
        return scored_path.parent / "reports" / "agent_radar_report.html"
    return project_path("outputs/reports/agent_radar_report.html")
