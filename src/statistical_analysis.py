from __future__ import annotations

from typing import Any

import pandas as pd

from .utils import project_path, write_json


def run_statistical_analysis(config: dict[str, Any]) -> dict[str, Any]:
    """Generate first-stage descriptive statistics and save Markdown/JSON."""
    paths = config["paths"]
    df = pd.read_csv(project_path(paths["scored_repos"]))
    numeric = ["stars_total", "forks_total", "open_issues_count", "readme_length", "final_potential_score", "risk_score"]
    summary = {
        "sample_size": int(len(df)),
        "source_type_counts": df["source_type"].value_counts(dropna=False).to_dict(),
        "api_live_ratio": float((df["source_type"] == "api_live").mean()) if len(df) else 0.0,
        "language_distribution": df["language"].value_counts().head(15).to_dict(),
        "describe": df[numeric].describe().round(3).to_dict(),
        "correlation": df[numeric].corr(numeric_only=True).round(3).fillna(0).to_dict(),
        "top_potential": df.sort_values("final_potential_score", ascending=False)[["full_name", "final_potential_score", "recommendation_level"]].head(10).to_dict("records"),
        "top_risk": df.sort_values("risk_score", ascending=False)[["full_name", "risk_score", "api_status"]].head(10).to_dict("records"),
    }
    write_json("outputs/reports/stat_summary.json", summary)
    md = [
        "# AgentRadar-Stat Statistical Summary",
        f"- Sample size: {summary['sample_size']}",
        f"- API live ratio: {summary['api_live_ratio']:.2%}",
        f"- Source types: {summary['source_type_counts']}",
        "## Top Potential Projects",
    ]
    for item in summary["top_potential"]:
        md.append(f"- {item['full_name']}: {item['final_potential_score']:.2f} ({item['recommendation_level']})")
    md.extend(["## Top Risk Projects"])
    for item in summary["top_risk"]:
        md.append(f"- {item['full_name']}: risk={item['risk_score']:.2f}, status={item['api_status']}")
    out = project_path("outputs/reports/stat_summary.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    return summary
