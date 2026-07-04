from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .utils import project_path


PALETTE = ["#38BDF8", "#22D3EE", "#60A5FA", "#10B981", "#F59E0B", "#EF4444"]
LEVEL_PALETTE = {"A": "#10B981", "B": "#38BDF8", "C": "#F59E0B", "D": "#EF4444"}


def generate_figures(config: dict[str, Any]) -> list[str]:
    """Generate static charts for trend, scoring, clustering, and model review."""
    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    if "cluster_label" in df.columns:
        df["cluster_plot_label"] = "Cluster " + df["cluster_label"].astype(str)
    out_dir = project_path(config["paths"].get("figures_dir", "outputs/figures"))
    out_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    sns.set_theme(style="whitegrid", palette=PALETTE)
    plt.rcParams.update(
        {
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#BAE6FD",
            "grid.color": "#E2F3FB",
            "text.color": "#1F2937",
            "axes.labelcolor": "#1F2937",
            "xtick.color": "#64748B",
            "ytick.color": "#64748B",
        }
    )

    def save(name: str) -> None:
        path = out_dir / name
        plt.tight_layout()
        plt.savefig(path, dpi=200, bbox_inches="tight")
        plt.close()
        generated.append(str(path))

    plt.figure(figsize=(7, 4))
    sns.histplot(df["stars_total"], bins=30, color="#38BDF8")
    plt.title("Stars Distribution")
    plt.xlabel("Stars")
    save("stars_distribution.png")

    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=df, x="stars_total", y="forks_total", hue="source_type", palette={"api_live": "#38BDF8", "sample_fallback": "#F59E0B"}, s=26)
    plt.title("Stars vs Forks")
    save("stars_forks_scatter.png")

    plt.figure(figsize=(7, 4))
    df["language"].value_counts().head(12).plot(kind="bar", color="#38BDF8")
    plt.title("Language Distribution")
    plt.ylabel("Repository count")
    save("language_distribution.png")

    numeric = ["stars_total", "forks_total", "open_issues_count", "readme_length", "final_potential_score", "risk_score"]
    plt.figure(figsize=(7, 5))
    sns.heatmap(df[numeric].corr(numeric_only=True), annot=True, fmt=".2f", cmap="Blues")
    plt.title("Metric Correlation Heatmap")
    save("correlation_heatmap.png")

    for column, filename, ascending in [
        ("final_potential_score", "top_potential.png", False),
        ("risk_score", "top_risk.png", False),
    ]:
        plt.figure(figsize=(8, 4))
        top = df.sort_values(column, ascending=ascending).head(10)
        sns.barplot(data=top, x=column, y="full_name", color="#38BDF8")
        plt.title(filename.replace("_", " ").replace(".png", "").title())
        save(filename)

    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=df, x="risk_score", y="final_potential_score", hue="recommendation_level", palette=LEVEL_PALETTE, s=32)
    plt.title("Risk-Potential Quadrant")
    save("risk_potential_quadrant.png")

    if {"pca_x", "pca_y", "cluster_plot_label"}.issubset(df.columns):
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=df, x="pca_x", y="pca_y", hue="cluster_plot_label", palette="Blues", s=34)
        plt.title("PCA/KMeans Cluster Map")
        save("pca_kmeans_cluster_scatter.png")

        plt.figure(figsize=(8, 4))
        df["cluster_plot_label"].value_counts().plot(kind="bar", color="#38BDF8")
        plt.title("Cluster Type Counts")
        plt.ylabel("Repository count")
        save("cluster_type_counts.png")

    plt.figure(figsize=(6, 4))
    df["recommendation_level"].value_counts().reindex(["A", "B", "C", "D"]).fillna(0).plot(kind="bar", color=[LEVEL_PALETTE[x] for x in ["A", "B", "C", "D"]])
    plt.title("Recommendation Level Distribution")
    plt.ylabel("Repository count")
    save("recommendation_distribution.png")

    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=df, x="readme_length", y="final_potential_score", hue="recommendation_level", palette=LEVEL_PALETTE, s=30)
    plt.title("README Length vs Final Potential Score")
    save("readme_score_relationship.png")

    metrics_path = project_path("outputs/reports/model_metrics_task_a.csv")
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path)
        matrix = [[0, 0], [0, 0]]
        if not metrics_df.empty and "confusion_matrix" in metrics_df.columns:
            best_row = metrics_df.sort_values("f1", ascending=False).iloc[0]
            try:
                import ast

                matrix = ast.literal_eval(str(best_row["confusion_matrix"]))
            except Exception:  # noqa: BLE001 - figure generation should continue.
                matrix = [[0, 0], [0, 0]]
        plt.figure(figsize=(4.5, 4))
        sns.heatmap(matrix, annot=True, fmt="g", cmap="Blues", cbar=False)
        plt.title("Task A Best Model Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        save("model_confusion_matrix.png")

    score_features = ["stars_per_day", "issue_pressure", "readme_length", "agent_relevance_score", "reproducibility_score", "risk_score"]
    importance = df[score_features + ["final_potential_score"]].corr(numeric_only=True)["final_potential_score"].drop("final_potential_score").abs().sort_values()
    plt.figure(figsize=(7, 4))
    importance.plot(kind="barh", color="#38BDF8")
    plt.title("Feature Importance Proxy")
    save("feature_importance_proxy.png")

    model_metrics_path = project_path("outputs/reports/model_metrics.csv")
    if model_metrics_path.exists():
        metrics_df = pd.read_csv(model_metrics_path)
        if {"model_name", "f1"}.issubset(metrics_df.columns):
            plt.figure(figsize=(7, 4))
            sns.barplot(data=metrics_df, x="model_name", y="f1", color="#38BDF8")
            plt.ylim(0, 1)
            plt.title("Model Comparison by F1")
            plt.xticks(rotation=20)
            save("model_comparison_f1.png")
    personalized_path = project_path("outputs/reports/personalized_recommendations.csv")
    if personalized_path.exists():
        personalized = pd.read_csv(personalized_path)
        if {"final_potential_score", "personalized_score"}.issubset(personalized.columns):
            plt.figure(figsize=(7, 5))
            sns.scatterplot(
                data=personalized,
                x="final_potential_score",
                y="personalized_score",
                hue="recommendation_level" if "recommendation_level" in personalized.columns else None,
                palette=LEVEL_PALETTE,
                s=36,
            )
            plt.title("Base Score vs Personalized Score")
            plt.xlabel("Final potential score")
            plt.ylabel("Personalized score")
            save("personalized_vs_base_score.png")
    return generated
