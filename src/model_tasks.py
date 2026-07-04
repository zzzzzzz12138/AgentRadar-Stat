from __future__ import annotations

from typing import Any

import pandas as pd

from .utils import project_path, write_json


LEAKAGE_COLUMNS = {
    "final_potential_score",
    "recommendation_level",
    "trend_score",
    "activity_score",
    "community_score",
    "documentation_score",
    "innovation_score",
    "feasibility_score",
}

NO_LEAKAGE_FEATURES = [
    "stars_total",
    "forks_total",
    "watchers_total",
    "open_issues_count",
    "size",
    "stars_this_week",
    "project_age_days",
    "days_since_update",
    "log_stars",
    "log_forks",
    "stars_per_day",
    "forks_per_star",
    "issue_pressure",
    "topic_count",
    "readme_length",
    "has_install_section",
    "has_quickstart",
    "has_demo",
    "has_example",
    "has_requirements",
    "mentions_gpu",
    "mentions_cpu",
    "mentions_api_key",
    "mentions_docker",
    "agent_keyword_count",
    "agent_relevance_score",
    "reproducibility_score",
]


def define_model_tasks(config: dict[str, Any]) -> pd.DataFrame:
    """Create task A/B labels and write label methodology reports."""
    path = project_path(config["paths"]["scored_repos"])
    df = pd.read_csv(path)
    labeled = add_model_task_labels(df)
    labeled.to_csv(path, index=False, encoding="utf-8-sig")
    clustered_path = project_path(config["paths"].get("clustered_repos", "data/processed/clustered_repos.csv"))
    if clustered_path.exists():
        labeled.to_csv(clustered_path, index=False, encoding="utf-8-sig")
    write_label_reports(labeled)
    return labeled


def add_model_task_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Add leakage-aware supervised labels for task A and task B."""
    data = df.copy()
    data["task_a_high_potential"] = data["recommendation_level"].isin(["A", "B"]).astype(int)
    low_star = data["stars_total"] <= data["stars_total"].quantile(0.55)
    growth = (data["stars_per_day"] >= data["stars_per_day"].quantile(0.70)) | (data["stars_this_week"] >= data["stars_this_week"].quantile(0.70))
    data["emerging_project_flag"] = (low_star & growth).astype(int)
    docs = data[["has_install_section", "has_quickstart", "has_demo", "has_example", "has_requirements"]].mean(axis=1) >= 0.55
    cpu_ok = (data["mentions_cpu"] > 0) | (data["mentions_gpu"] == 0)
    low_risk = data["risk_score"] <= data["risk_score"].quantile(0.55)
    data["reproduction_friendly_flag"] = (docs & cpu_ok & low_risk).astype(int)
    attention = data["trend_score"] >= data["trend_score"].quantile(0.60)
    data["high_attention_low_risk_flag"] = (attention & low_risk).astype(int)
    data["task_b_proxy_good_project"] = (
        (data["emerging_project_flag"] + data["reproduction_friendly_flag"] + data["high_attention_low_risk_flag"]) >= 1
    ).astype(int)
    return data


def write_label_reports(df: pd.DataFrame) -> None:
    """Persist label definitions and label distribution diagnostics."""
    distribution = {
        column: df[column].value_counts().sort_index().to_dict()
        for column in [
            "task_a_high_potential",
            "emerging_project_flag",
            "reproduction_friendly_flag",
            "high_attention_low_risk_flag",
            "task_b_proxy_good_project",
        ]
        if column in df.columns
    }
    write_json("outputs/reports/label_distribution.json", distribution)
    md = [
        "# Label Definition Report",
        "## Task A: scoring-system proxy model",
        "Task A predicts whether `recommendation_level` is A/B. It is used to explain the scoring boundary, not to claim future project success.",
        "Leakage control: model inputs must not include `final_potential_score`, `recommendation_level`, or sub-score fields such as `trend_score` and `documentation_score`.",
        "## Task B: project-potential proxy model",
        "Task B predicts `task_b_proxy_good_project`, built from emerging growth, reproduction friendliness, and high-attention-low-risk signals.",
        "This label is still a proxy, but it is less circular than directly predicting the score-generated recommendation level.",
        "## Label distributions",
    ]
    for name, values in distribution.items():
        md.append(f"- {name}: {values}")
    project_path("outputs/reports/label_definition_report.md").write_text("\n".join(md), encoding="utf-8")

