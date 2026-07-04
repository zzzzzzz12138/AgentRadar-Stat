from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .utils import project_path


AGENT_KEYWORDS = [
    "agent",
    "ai agent",
    "agentic",
    "autonomous",
    "multi-agent",
    "rag",
    "llm",
    "llmops",
    "mcp",
    "model context protocol",
    "coding",
    "code agent",
    "workflow",
    "browser",
    "research",
    "data agent",
    "automl",
    "multimodal",
    "copilot",
    "codex",
    "autogen",
    "crewai",
    "semantic kernel",
    "computer use",
    "assistant",
]


def build_features(config: dict[str, Any]) -> pd.DataFrame:
    """Build first-stage numerical and text features."""
    paths = config["paths"]
    df = pd.read_csv(project_path(paths["cleaned_repos"]))
    df = add_features(df)
    out_path = project_path(paths["feature_repos"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a feature-enriched dataframe without mutating callers."""
    data = df.copy()
    now = pd.Timestamp.utcnow()
    created = pd.to_datetime(data["created_at"], errors="coerce", utc=True).fillna(now)
    pushed = pd.to_datetime(data["pushed_at"], errors="coerce", utc=True).fillna(now)
    data["project_age_days"] = (now - created).dt.days.clip(lower=1)
    data["days_since_update"] = (now - pushed).dt.days.clip(lower=0)
    data["log_stars"] = np.log1p(pd.to_numeric(data["stars_total"], errors="coerce").fillna(0))
    data["log_forks"] = np.log1p(pd.to_numeric(data["forks_total"], errors="coerce").fillna(0))
    data["stars_per_day"] = data["stars_total"] / data["project_age_days"].replace(0, 1)
    data["forks_per_star"] = data["forks_total"] / data["stars_total"].replace(0, 1)
    data["issue_pressure"] = data["open_issues_count"] / (data["stars_total"] + 1)
    data["topic_count"] = data["topics"].fillna("").astype(str).apply(lambda x: len([t for t in x.replace(",", "|").split("|") if t.strip()]))
    readme = data["readme_text"].fillna("").astype(str)
    readme_lower = readme.str.lower()
    data["readme_length"] = readme.str.len()
    data["has_install_section"] = readme_lower.str.contains("install|installation|pip install|conda").astype(int)
    data["has_quickstart"] = readme_lower.str.contains("quickstart|quick start|get started").astype(int)
    data["has_demo"] = readme_lower.str.contains("demo|screenshot|example app").astype(int)
    data["has_example"] = readme_lower.str.contains("example|examples|usage").astype(int)
    data["has_requirements"] = readme_lower.str.contains("requirements|pyproject|environment.yml").astype(int)
    data["mentions_gpu"] = readme_lower.str.contains("gpu|cuda|vram").astype(int)
    data["mentions_cpu"] = readme_lower.str.contains("cpu|cpu-only|no gpu").astype(int)
    data["mentions_api_key"] = readme_lower.str.contains("api key|apikey|token|secret").astype(int)
    data["mentions_docker"] = readme_lower.str.contains("docker|container").astype(int)
    combined = (
        data["repo_name"].fillna("").astype(str)
        + " "
        + data["description"].fillna("").astype(str)
        + " "
        + data["topics"].fillna("").astype(str)
        + " "
        + readme_lower
    ).str.lower()
    data["agent_keyword_count"] = combined.apply(lambda text: sum(text.count(k) for k in AGENT_KEYWORDS))
    data["agent_relevance_score"] = (data["agent_keyword_count"] / max(1, len(AGENT_KEYWORDS))).clip(0, 1)
    doc_bits = ["has_install_section", "has_quickstart", "has_demo", "has_example", "has_requirements", "mentions_cpu", "mentions_docker"]
    data["reproducibility_score"] = data[doc_bits].mean(axis=1)
    data["risk_score"] = (
        (data["days_since_update"] > 365).astype(int) * 0.25
        + (data["issue_pressure"] > data["issue_pressure"].quantile(0.75)).astype(int) * 0.25
        + (data["readme_length"] < 400).astype(int) * 0.20
        + data["mentions_gpu"] * 0.15
        + data["mentions_api_key"] * 0.15
    ).clip(0, 1)
    return data
