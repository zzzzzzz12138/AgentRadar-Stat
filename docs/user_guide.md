# User Guide

## Basic run

1. Configure `.env` from `.env.example`. Do not commit real keys.
2. Run `python main.py`.
3. Open `streamlit run app.py`.
4. Review `outputs/reports/agent_radar_report.html`, `outputs/reports/agent_radar_report.pdf`, and `outputs/dashboards/agent_radar_dashboard.html`.

## Personalization

Use the sidebar profile form in Streamlit, then open `个性化推荐`. The app shows personalized ranking, score comparison, match reasons, risk warnings, a three-day route, a Codex prompt, and popular projects that are less suitable for the profile.

## Showcase Pages

- 首页 / 项目概览: report-style hero, capability flow, KPI cards, score explorer, and curated project cards.
- 数据采集: sample construction cards, four-stage collection funnel, and sample-building path.
- 指标体系: seven-dimension scoring framework and personalization mechanism.
- 趋势洞察: one scope control updates language, Stars, Stars-Forks, technology themes, and project cards together.
- 评分排行: two-row filters, risk-potential quadrant, score explorer, and project cards.
- 聚类画像: PCA project map, cluster counts, method comparison, and representative project cards for every cluster.
- 模型预测: separate Task A and Task B tabs, leakage-control note, model comparison, results, and task-specific feature importance.
- PyTorch 扩展: TabularWideDeepNet architecture, blue training curves, and validation/test metrics.
- 个性化推荐: synchronized profile summary, score charts, explanation-first project cards, risks, route, and Codex prompt.
- DeepSeek Agent: seven full-width evidence-grounded Agent cards without raw payload display.
- 单项目详情: repository summary, seven-dimension scores, compact README signals, and cached Agent explanation.
- 项目亮点 / 局限展望: project workload, evidence boundaries, and future extensions.
- 报告导出: downloads `outputs/reports/agent_radar_report.pdf` and the interactive HTML report.

## Final report and big screen

- The final HTML report has a clickable table of contents, Chinese section titles, KPI cards, method flow, metric system, interactive Plotly charts, model rigor sections, personalized recommendations, and DeepSeek Agent cards.
- The final big screen is a compact defense dashboard: KPI strip, risk-potential quadrant, PCA cluster map, Top rankings, collection funnel, recommendation donut, cluster type distribution, and model comparison.
- The report and Streamlit describe the sample as GitHub public repository data; emergency local-sample status is kept in technical outputs only.
- The PDF is generated automatically when Playwright and Chromium are available. If it is missing, install:

```powershell
python -m pip install playwright
python -m playwright install chromium
python main.py
```

## Model outputs

- `outputs/reports/label_definition_report.md`
- `outputs/reports/cluster_model_comparison.csv`
- `outputs/reports/model_card.md`
- `outputs/reports/torch_model_card.md`
- `outputs/reports/personalized_recommendations.csv`
- `outputs/screenshots/README.md`
