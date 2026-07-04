# Model Card

## Task definitions

- Task A: scoring-system proxy model; label is A/B recommendation level. Purpose is scoring-rule explanation.

- Task B: project-potential proxy model; label combines emerging, reproduction-friendly, and high-attention-low-risk signals.

## Leakage control

Inputs exclude `final_potential_score`, `recommendation_level`, and sub-score fields directly used by scoring.

## Feature set

stars_total, forks_total, watchers_total, open_issues_count, size, stars_this_week, project_age_days, days_since_update, log_stars, log_forks, stars_per_day, forks_per_star, issue_pressure, topic_count, readme_length, has_install_section, has_quickstart, has_demo, has_example, has_requirements, mentions_gpu, mentions_cpu, mentions_api_key, mentions_docker, agent_keyword_count, agent_relevance_score, reproducibility_score

## Model selection

Compared Dummy, Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and calibrated Random Forest with stratified CV.

Best Task A model: logistic_regression (F1=0.941)

Best Task B model: gradient_boosting (F1=0.980)

## Boundaries

Proxy models over public GitHub metadata and README-derived signals; not forecasts of commercial value or future popularity.