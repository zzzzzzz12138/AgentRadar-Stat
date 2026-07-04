# Agent Instructions

This repository is a staged Python data science project. Preserve the project structure and keep code modular.

Rules for future coding agents:

1. Do not hardcode `GITHUB_TOKEN`, `DEEPSEEK_API_KEY`, or any private credential.
2. Read secrets only from `.env` or environment variables.
3. Real GitHub API collection is the primary data flow.
4. `data/sample/sample_trending_projects.csv` is fallback-only and must not be deleted.
5. DeepSeek agents should attempt real API calls first when enabled and fall back only when disabled, missing keys, or failed calls.
6. Keep logic out of `app.py`; Streamlit should call or read outputs from `src/` modules.
7. Add docstrings for important functions. Chinese comments are welcome where they clarify data-processing steps.
8. After changing code, run `python main.py` or targeted tests, then run `pytest` when feasible.
9. Update `README.md` when adding user-facing commands, outputs, or configuration.
10. Prioritize Windows 11, Python 3.10, CPU-only, PyTorch-compatible execution.
11. Protect `.env`: never read, print, commit, or serialize real key values.
12. DeepSeek output is explanatory evidence, not the fact source. Final claims must bind to fields, figures, model metrics, or report tables.
13. New features must be connected to `main.py`, tested, and documented.
14. Preserve fallback data and API-first behavior when changing collection logic.
15. Frontend pages must not display raw Agent JSON by default; use `src/agent_display.py` normalization and card rendering.
16. Keep the ice-blue visual system consistent across Streamlit, HTML report, dashboard, and charts.

16. Modeling additions must keep Task A and Task B separate and must not train on `final_potential_score`, `recommendation_level`, score-component fields, or other direct leakage fields.
17. User profiles must remain local preference objects only. Do not add available-time, budget, private identity, or credential fields.
18. Personalization outputs must include reasons, risks, route suggestions, and Codex prompts while remaining grounded in repository fields.
19. PyTorch models must stay CPU-compatible and failure-tolerant in `main.py`.
20. Showcase UI work should reuse `src/theme.py`, `src/ui_components.py`, and `src/agent_display.py`; do not reintroduce raw JSON display.
21. Presentation changes should preserve the existing pipeline and validate with `python main.py` or targeted tests when feasible.
22. Keep screenshot materials under `outputs/screenshots/` and never capture or expose `.env` contents.
23. Final showcase report and dashboard should use `src/interactive_visualization.py` Plotly fragments, Chinese display labels, `assets/agent_radar_bg.svg`, and optional `src/pdf_exporter.py`; do not reintroduce PNG-only report charts or ISO timestamps in defense-facing pages.
24. Streamlit showcase pages should reuse `src/streamlit_theme.py` and `src/streamlit_components.py`; keep navigation, filters, charts, cards, Agent output, and report export Chinese-first and presentation-oriented.
25. Streamlit pages should not show debugging labels, raw field names, raw Agent JSON, local absolute paths, key configuration status, or generated timestamps as user-facing content.
