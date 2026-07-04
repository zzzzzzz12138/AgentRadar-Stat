# Model Methodology

## Why the project does not blindly chase complex models

AgentRadar-Stat is built for a small-to-medium GitHub metadata table. The project needs transparent decisions for course review: why a repository ranks well, what risks exist, and whether it fits a user profile. For that reason, the pipeline compares simple baselines, tree models, calibrated models, clustering methods, and a CPU-friendly PyTorch tabular model instead of claiming that a larger model is automatically better.

## Task A: scoring-system proxy

Task A predicts whether `recommendation_level` is A/B. This is not a future-success label. It is a proxy for explaining whether the current scoring system is dominated by a few low-level variables.

Leakage control: Task A excludes `final_potential_score`, `recommendation_level`, and score-component columns from the feature set.

## Task B: project-potential proxy

Task B predicts `task_b_proxy_good_project`, a proxy label built from emerging growth, reproduction friendliness, and high-attention-low-risk signals. It is closer to project selection than Task A, but it is still a proxy and must not be interpreted as ground truth.

## Feature groups

- `raw_features`: stars, forks, watchers, open issues, project age, update delay, size, weekly stars.
- `text_signal_features`: README length, install/demo/example signals, CPU/GPU/API-key mentions, topic count, agent keyword count.
- `score_features`: scoring sub-scores, useful for reporting but excluded from leakage-controlled supervised training.
- `no_leakage_features`: raw and low-level derived fields only; excludes `final_potential_score`, `recommendation_level`, score components, and `risk_score` because risk is part of the Task B high-attention-low-risk proxy.

## Clustering methodology

Clustering is used to create project type profiles, not supervised predictions. The pipeline compares KMeans, Gaussian Mixture, Agglomerative Clustering, and DBSCAN diagnostics. K values from 3 to 8 are evaluated with silhouette score, Calinski-Harabasz, Davies-Bouldin, plus GMM AIC/BIC. The final selection uses a combined selection score and writes the rationale to `cluster_summary.md`.

The cluster output supports personalization by identifying project types such as mature high-attention projects, emerging projects, documentation-friendly projects, niche tools, and conceptually novel but less mature projects.

## Model comparison and calibration

Task A and Task B each compare Dummy, Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and calibrated Random Forest. Outputs include cross-validation, threshold analysis, calibration curve data, Brier score, feature importance, and permutation importance. Probability-like outputs are model confidence scores, not true probabilities of future success.

## PyTorch tabular model

`TabularWideDeepNet` keeps the baseline MLP but adds numeric branches, categorical embeddings, a wide branch, dropout, AdamW, early stopping, and gradient clipping. It remains CPU-only and is treated as an extension experiment. If sklearn models perform better, the report should say so directly.

## Personalization

The user profile is local session data. It contains role, goal, programming level, preferred languages/topics, hardware condition, risk preference, and output preference. It does not contain private identity, available time, or API budget. Personalized ranking adjusts the generic score with preference, feasibility, goal, language, topic, hardware, and risk components.
