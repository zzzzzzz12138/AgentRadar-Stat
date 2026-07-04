from __future__ import annotations

import os
from typing import Any

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .utils import project_path, write_json


os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")


CLUSTER_FEATURES = [
    "log_stars",
    "log_forks",
    "stars_per_day",
    "forks_per_star",
    "issue_pressure",
    "topic_count",
    "readme_length",
    "agent_relevance_score",
    "reproducibility_score",
    "trend_score",
    "activity_score",
    "community_score",
    "documentation_score",
    "innovation_score",
    "feasibility_score",
    "risk_score",
    "final_potential_score",
]

CLUSTER_NAMES = {
    "hot_mature": "高热度成熟型",
    "emerging": "新兴爆发潜力型",
    "reproducible": "文档完善可复现型",
    "risky_star": "高 star 低维护风险型",
    "immature": "概念新颖但工程不成熟型",
}


def run_clustering(config: dict[str, Any], k: int = 5) -> pd.DataFrame:
    """Run PCA and KMeans, persist clustered data, and merge fields into scored data."""
    paths = config["paths"]
    scored_path = project_path(paths["scored_repos"])
    df = pd.read_csv(scored_path)
    clustered = add_cluster_fields(df, k=k)

    clustered_path = project_path(paths.get("clustered_repos", "data/processed/clustered_repos.csv"))
    clustered_path.parent.mkdir(parents=True, exist_ok=True)
    clustered.to_csv(clustered_path, index=False, encoding="utf-8-sig")
    clustered.to_csv(scored_path, index=False, encoding="utf-8-sig")
    save_cluster_summary(clustered)
    return clustered


def add_cluster_fields(df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """Add pca_x, pca_y, explained variance, cluster_label, and cluster_name."""
    data = df.copy()
    features = [col for col in CLUSTER_FEATURES if col in data.columns]
    X = data[features].apply(pd.to_numeric, errors="coerce").fillna(0)
    if len(data) < 2 or not features:
        data["pca_x"] = 0.0
        data["pca_y"] = 0.0
        data["pca_explained_var_1"] = 0.0
        data["pca_explained_var_2"] = 0.0
        data["cluster_label"] = 0
        data["cluster_name"] = CLUSTER_NAMES["immature"]
        return data

    scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    data["pca_x"] = coords[:, 0]
    data["pca_y"] = coords[:, 1]
    data["pca_explained_var_1"] = float(pca.explained_variance_ratio_[0])
    data["pca_explained_var_2"] = float(pca.explained_variance_ratio_[1])

    n_clusters = max(1, min(k, len(data)))
    labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(scaled)
    data["cluster_label"] = labels
    data["cluster_name"] = _name_clusters(data)
    return data


def _name_clusters(df: pd.DataFrame) -> pd.Series:
    names: dict[int, str] = {}
    global_star = df["trend_score"].median()
    global_risk = df["risk_score"].median()
    global_doc = df["documentation_score"].median()
    global_update = df["activity_score"].median()
    for label, group in df.groupby("cluster_label"):
        trend = group["trend_score"].mean()
        risk = group["risk_score"].mean()
        doc = group["documentation_score"].mean()
        activity = group["activity_score"].mean()
        potential = group["final_potential_score"].mean()
        if trend >= global_star and activity >= global_update and risk <= global_risk:
            names[label] = CLUSTER_NAMES["hot_mature"]
        elif potential >= df["final_potential_score"].quantile(0.65) and trend < global_star:
            names[label] = CLUSTER_NAMES["emerging"]
        elif doc >= global_doc and risk <= global_risk:
            names[label] = CLUSTER_NAMES["reproducible"]
        elif trend >= global_star and risk > global_risk and activity < global_update:
            names[label] = CLUSTER_NAMES["risky_star"]
        else:
            names[label] = CLUSTER_NAMES["immature"]
    return df["cluster_label"].map(names)


def save_cluster_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Save cluster summary as JSON and Markdown."""
    summary = {
        "cluster_count": int(df["cluster_label"].nunique()),
        "pca_explained_var_1": float(df["pca_explained_var_1"].iloc[0]) if len(df) else 0.0,
        "pca_explained_var_2": float(df["pca_explained_var_2"].iloc[0]) if len(df) else 0.0,
        "clusters": [],
    }
    for label, group in df.groupby("cluster_label"):
        summary["clusters"].append(
            {
                "cluster_label": int(label),
                "cluster_name": str(group["cluster_name"].iloc[0]),
                "count": int(len(group)),
                "avg_final_potential_score": float(group["final_potential_score"].mean()),
                "avg_risk_score": float(group["risk_score"].mean()),
                "representative_projects": group.sort_values("final_potential_score", ascending=False)["full_name"].head(5).tolist(),
            }
        )
    write_json("outputs/reports/cluster_summary.json", summary)
    md = [
        "# PCA/KMeans Cluster Summary",
        f"- Clusters: {summary['cluster_count']}",
        f"- PCA explained variance: {summary['pca_explained_var_1']:.3f}, {summary['pca_explained_var_2']:.3f}",
    ]
    for item in summary["clusters"]:
        md.append(f"## {item['cluster_label']} - {item['cluster_name']}")
        md.append(f"- Count: {item['count']}")
        md.append(f"- Avg potential: {item['avg_final_potential_score']:.2f}")
        md.append(f"- Avg risk: {item['avg_risk_score']:.2f}")
        md.append(f"- Representatives: {', '.join(item['representative_projects'])}")
    out = project_path("outputs/reports/cluster_summary.md")
    out.write_text("\n".join(md), encoding="utf-8")
    return summary
