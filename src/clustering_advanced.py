from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from .clustering import CLUSTER_FEATURES
from .utils import project_path, write_json


os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")


def run_advanced_clustering(config: dict[str, Any]) -> pd.DataFrame:
    """Compare clustering algorithms, select a final model, and profile clusters."""
    path = project_path(config["paths"]["scored_repos"])
    df = pd.read_csv(path)
    features = [col for col in CLUSTER_FEATURES if col in df.columns]
    X = df[features].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaled = StandardScaler().fit_transform(X)
    comparison = compare_cluster_models(scaled)
    comparison.to_csv(project_path("outputs/reports/cluster_model_comparison.csv"), index=False, encoding="utf-8-sig")
    best = choose_best_cluster_model(comparison)
    labels = fit_final_labels(scaled, best)
    clustered = attach_cluster_outputs(df, scaled, labels)
    profile = build_cluster_profile(clustered)
    profile.to_csv(project_path("outputs/reports/cluster_profile.csv"), index=False, encoding="utf-8-sig")
    stability = compute_kmeans_stability(scaled, int(best.get("k", 5)))
    stability["best_cluster_model"] = best
    write_json("outputs/reports/cluster_stability.json", stability)
    write_cluster_summary(best, profile, stability)
    clustered_path = project_path(config["paths"].get("clustered_repos", "data/processed/clustered_repos.csv"))
    clustered.to_csv(clustered_path, index=False, encoding="utf-8-sig")
    clustered.to_csv(path, index=False, encoding="utf-8-sig")
    return clustered


def compare_cluster_models(scaled: np.ndarray) -> pd.DataFrame:
    """Return metrics for KMeans, GMM, Agglomerative, and DBSCAN diagnostics."""
    rows: list[dict[str, Any]] = []
    n = len(scaled)
    for k in range(3, min(8, n - 1) + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
        rows.append(_cluster_metrics("kmeans", k, km, scaled))
        gm_model = GaussianMixture(n_components=k, random_state=42)
        gm = gm_model.fit_predict(scaled)
        row = _cluster_metrics("gaussian_mixture", k, gm, scaled)
        row["bic"] = float(gm_model.bic(scaled))
        row["aic"] = float(gm_model.aic(scaled))
        rows.append(row)
        agg = AgglomerativeClustering(n_clusters=k).fit_predict(scaled)
        rows.append(_cluster_metrics("agglomerative", k, agg, scaled))
    try:
        db = DBSCAN(eps=1.5, min_samples=5).fit_predict(scaled)
        rows.append(_cluster_metrics("dbscan_diagnostic", int(len(set(db)) - (1 if -1 in db else 0)), db, scaled))
    except Exception as exc:  # noqa: BLE001
        rows.append({"model": "dbscan_diagnostic", "k": None, "error": str(exc)})
    comparison = pd.DataFrame(rows)
    comparison["selection_score"] = comparison["silhouette"].fillna(-1) + comparison["calinski_harabasz"].fillna(0) / 10000 - comparison["davies_bouldin"].fillna(10) / 100
    return comparison


def _cluster_metrics(model: str, k: int, labels: np.ndarray, scaled: np.ndarray) -> dict[str, Any]:
    unique = set(labels)
    valid = len(unique - {-1}) >= 2
    row = {"model": model, "k": int(k), "n_clusters_observed": int(len(unique - {-1}))}
    if valid:
        row.update(
            {
                "silhouette": float(silhouette_score(scaled, labels)),
                "calinski_harabasz": float(calinski_harabasz_score(scaled, labels)),
                "davies_bouldin": float(davies_bouldin_score(scaled, labels)),
            }
        )
    else:
        row.update({"silhouette": np.nan, "calinski_harabasz": np.nan, "davies_bouldin": np.nan})
    return row


def choose_best_cluster_model(comparison: pd.DataFrame) -> dict[str, Any]:
    candidates = comparison[comparison["model"].isin(["kmeans", "gaussian_mixture", "agglomerative"])].dropna(subset=["silhouette"])
    if candidates.empty:
        return {"model": "kmeans", "k": 5, "reason": "fallback because no valid comparison metric was available", "selection_score": None}
    best = candidates.sort_values(["selection_score", "silhouette", "calinski_harabasz"], ascending=[False, False, False]).iloc[0].to_dict()
    best["reason"] = "selected by combined selection_score: silhouette first, Calinski-Harabasz reward, Davies-Bouldin penalty"
    return best


def fit_final_labels(scaled: np.ndarray, best: dict[str, Any]) -> np.ndarray:
    model = best.get("model", "kmeans")
    k = int(best.get("k") or 5)
    if model == "gaussian_mixture":
        return GaussianMixture(n_components=k, random_state=42).fit_predict(scaled)
    if model == "agglomerative":
        return AgglomerativeClustering(n_clusters=k).fit_predict(scaled)
    return KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)


def attach_cluster_outputs(df: pd.DataFrame, scaled: np.ndarray, labels: np.ndarray) -> pd.DataFrame:
    data = df.copy()
    coords = PCA(n_components=2, random_state=42).fit_transform(scaled)
    data["pca_x"] = coords[:, 0]
    data["pca_y"] = coords[:, 1]
    data["cluster_label"] = labels
    profile_names = _profile_names(data)
    data["cluster_name"] = data["cluster_label"].map(profile_names)
    return data


def _profile_names(df: pd.DataFrame) -> dict[int, str]:
    names: dict[int, str] = {}
    for label, group in df.groupby("cluster_label"):
        stars = group["stars_total"].mean()
        risk = group["risk_score"].mean()
        docs = group["readme_length"].mean()
        update = group["days_since_update"].mean()
        growth = group["stars_per_day"].mean()
        if stars >= df["stars_total"].quantile(0.70) and update <= df["days_since_update"].median() and risk <= df["risk_score"].median():
            name = "高热度成熟型"
        elif growth >= df["stars_per_day"].quantile(0.70) and stars <= df["stars_total"].quantile(0.60):
            name = "新兴爆发潜力型"
        elif docs >= df["readme_length"].quantile(0.65) and risk <= df["risk_score"].median():
            name = "文档完善可复现型"
        elif stars >= df["stars_total"].quantile(0.65) and (update > df["days_since_update"].median() or risk > df["risk_score"].median()):
            name = "高 star 低维护风险型"
        elif group["topic_count"].mean() <= df["topic_count"].median():
            name = "小众垂直工具型"
        else:
            name = "概念新颖但工程不成熟型"
        names[int(label)] = name
    return names


def build_cluster_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, group in df.groupby("cluster_label"):
        topics = group.get("topics", pd.Series("", index=group.index)).fillna("").str.replace(",", "|").str.split("|").explode().str.strip()
        rows.append(
            {
                "cluster_label": int(label),
                "cluster_name": group["cluster_name"].iloc[0],
                "count": int(len(group)),
                "avg_final_potential_score": float(group["final_potential_score"].mean()),
                "avg_risk_score": float(group["risk_score"].mean()),
                "avg_stars_total": float(group["stars_total"].mean()),
                "avg_days_since_update": float(group["days_since_update"].mean()),
                "avg_readme_length": float(group["readme_length"].mean()),
                "top_language": group["language"].mode().iloc[0] if not group["language"].mode().empty else "Unknown",
                "top_topic": topics[topics != ""].mode().iloc[0] if not topics[topics != ""].mode().empty else "Unknown",
                "recommendation_distribution": group["recommendation_level"].value_counts().to_dict(),
                "representative_projects": "; ".join(group.sort_values("final_potential_score", ascending=False)["full_name"].head(5)),
            }
        )
    return pd.DataFrame(rows)


def compute_kmeans_stability(scaled: np.ndarray, k: int) -> dict[str, Any]:
    labels = [KMeans(n_clusters=k, random_state=seed, n_init=10).fit_predict(scaled) for seed in [1, 7, 21, 42, 99]]
    ari = [adjusted_rand_score(labels[0], other) for other in labels[1:]]
    return {"method": "Adjusted Rand Index across KMeans seeds", "mean_ari": float(np.mean(ari)), "min_ari": float(np.min(ari)), "max_ari": float(np.max(ari))}


def write_cluster_summary(best: dict[str, Any], profile: pd.DataFrame, stability: dict[str, Any]) -> None:
    md = [
        "# Advanced Cluster Summary",
        f"- Best model: {best.get('model')} k={best.get('k')}",
        f"- Selection score: {best.get('selection_score')}",
        f"- Selection reason: {best.get('reason')}",
        f"- Stability mean ARI: {stability.get('mean_ari'):.3f}",
        "## Cluster Profiles",
    ]
    for _, row in profile.iterrows():
        md.extend(
            [
                f"### {row['cluster_label']} - {row['cluster_name']}",
                f"- Count: {row['count']}",
                f"- Avg potential: {row['avg_final_potential_score']:.2f}",
                f"- Avg risk: {row['avg_risk_score']:.2f}",
                f"- Representatives: {row['representative_projects']}",
            ]
        )
    project_path("outputs/reports/cluster_summary.md").write_text("\n".join(md), encoding="utf-8")
