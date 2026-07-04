# Development Log

## Modeling and personalization upgrade

- Added leakage-aware Task A and Task B label definitions.
- Added advanced clustering comparison and cluster profiles.
- Expanded sklearn model comparison with calibration, threshold analysis, feature importance, and model cards.
- Added CPU-friendly PyTorch TabularWideDeepNet while preserving baseline MLP.
- Added local user profile, personalized scoring, recommendation outputs, and Streamlit onboarding.
- Updated DeepSeek agent inputs to include user profile and personalized recommendation evidence.
- Preserved GitHub API-first collection, sample fallback, DeepSeek fallback, and `.env` protection.

## Showcase UI and report polish

- Rebuilt Streamlit as a product-style dashboard while keeping the core pipeline unchanged.
- Added shared `src/theme.py` and strengthened `src/ui_components.py` for consistent ice-blue cards, badges, and tables.
- Rewrote the HTML report as a final course artifact with executive summary, KPI cards, model sections, personalization, and Agent cards.
- Upgraded the HTML big screen with KPI strip, chart grid, personalized chart, model card, Agent status, and API status.
- Added `outputs/screenshots/` and screenshot checklist docs for classroom presentation.

## Showcase HTML, visualization, and PDF overhaul

- Rebuilt the HTML report as a Chinese defense-grade artifact with a clickable table of contents, richer KPI cards, method flow, metric system, model rigor, personalization, and Agent explanation sections.
- Rebuilt the HTML big screen as a compact defense cockpit with Chinese KPI labels, risk-potential quadrant, PCA cluster map, Top rankings, collection funnel, recommendation donut, cluster distribution, and model comparison.
- Added `src/interactive_visualization.py` so report and big screen use Plotly interactive charts instead of embedded PNG figures.
- Added `assets/agent_radar_bg.svg` and reused the ice-blue radar/network visual system across HTML and Streamlit.
- Added `src/pdf_exporter.py`; `python main.py` now attempts optional Playwright PDF export to `outputs/reports/agent_radar_report.pdf` without blocking the pipeline when dependencies are missing.
- Updated Streamlit report export page with PDF status, file size, download button, and open commands.

## Streamlit showcase overhaul

- Added `src/streamlit_theme.py` for report-matched Streamlit CSS, Chinese/serif typography, ice-blue component styling, and Plotly hover polish.
- Added `src/streamlit_components.py` for reusable KPI cards, capability flow, project cards, wide tables, progress bars, profile summaries, and Agent cards.
- Rebuilt `app.py` into ten Chinese showcase pages: 首页、数据概览、趋势洞察、评分排行、个性化推荐、聚类画像、模型预测、DeepSeek Agent、单项目详情、报告导出.
- Replaced narrow tables with project cards or wide tables to avoid vertical Chinese text.
- Replaced debugging-oriented status panels with data overview cards, funnel chart, and safe configuration note.
- Kept the modeling, collection, scoring, clustering, personalization, and Agent pipeline logic unchanged.
