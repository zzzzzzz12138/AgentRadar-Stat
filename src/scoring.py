from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from .utils import project_path


def score_projects(config: dict[str, Any]) -> pd.DataFrame:
    """Compute composite project scores and recommendation levels."""
    paths = config["paths"]
    df = pd.read_csv(project_path(paths["feature_repos"]))
    df = add_scores(df, config.get("scoring", {}).get("weights", {}))
    out_path = project_path(paths["scored_repos"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return df


def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    """Scale a series to 0-100 with robust empty handling."""
    values = pd.to_numeric(series, errors="coerce").fillna(0).to_numpy().reshape(-1, 1)
    if len(values) == 0 or float(values.max()) == float(values.min()):
        scaled = np.zeros(len(values))
    else:
        scaled = MinMaxScaler().fit_transform(values).ravel()
    if invert:
        scaled = 1 - scaled
    return pd.Series(scaled * 100, index=series.index)


def add_scores(df: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Add score columns and A/B/C/D recommendation levels."""
    data = df.copy()
    data["trend_score"] = (minmax(data["log_stars"]) * 0.55 + minmax(data["stars_this_week"]) * 0.45)
    data["activity_score"] = minmax(data["days_since_update"], invert=True)
    data["community_score"] = (minmax(data["log_forks"]) * 0.45 + minmax(data["watchers_total"]) * 0.35 + minmax(data["issue_pressure"], invert=True) * 0.20)
    data["documentation_score"] = (minmax(data["readme_length"]) * 0.45 + data[["has_install_section", "has_quickstart", "has_demo", "has_example", "has_requirements"]].mean(axis=1) * 55)
    data["innovation_score"] = (minmax(data["agent_keyword_count"]) * 0.55 + minmax(data["topic_count"]) * 0.45)
    data["feasibility_score"] = data["reproducibility_score"] * 100
    data["risk_score"] = pd.to_numeric(data["risk_score"], errors="coerce").fillna(0) * 100
    default_weights = {
        "trend_score": 0.25,
        "activity_score": 0.20,
        "community_score": 0.15,
        "documentation_score": 0.15,
        "innovation_score": 0.15,
        "feasibility_score": 0.10,
        "risk_score": -0.10,
    }
    default_weights.update(weights or {})
    data["final_potential_score"] = sum(data[col] * weight for col, weight in default_weights.items()).clip(0, 100)
    ranks = data["final_potential_score"].rank(pct=True)
    data["recommendation_level"] = pd.cut(ranks, bins=[0, 0.25, 0.55, 0.80, 1.0], labels=["D", "C", "B", "A"], include_lowest=True)
    return data
