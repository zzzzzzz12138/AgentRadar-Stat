# Label Definition Report
## Task A: scoring-system proxy model
Task A predicts whether `recommendation_level` is A/B. It is used to explain the scoring boundary, not to claim future project success.
Leakage control: model inputs must not include `final_potential_score`, `recommendation_level`, or sub-score fields such as `trend_score` and `documentation_score`.
## Task B: project-potential proxy model
Task B predicts `task_b_proxy_good_project`, built from emerging growth, reproduction friendliness, and high-attention-low-risk signals.
This label is still a proxy, but it is less circular than directly predicting the score-generated recommendation level.
## Label distributions
- task_a_high_potential: {0: 82, 1: 68}
- emerging_project_flag: {0: 124, 1: 26}
- reproduction_friendly_flag: {0: 64, 1: 86}
- high_attention_low_risk_flag: {0: 117, 1: 33}
- task_b_proxy_good_project: {0: 56, 1: 94}