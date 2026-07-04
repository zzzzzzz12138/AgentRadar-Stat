from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.agents import run_agents
from src.clustering_advanced import run_advanced_clustering
from src.dashboard import generate_dashboard
from src.data_clean import clean_data
from src.data_collect import collect_data
from src.feature_engineering import build_features
from src.model_tasks import define_model_tasks
from src.modeling import train_models
from src.pdf_exporter import export_report_pdf
from src.recommendation_engine import generate_personalized_recommendations
from src.report_generator import generate_report
from src.scoring import score_projects
from src.statistical_analysis import run_statistical_analysis
from src.torch_mlp import train_torch_mlp
from src.torch_tabular import train_torch_tabular
from src.user_profile import default_user_profile
from src.utils import ensure_directories, load_config, setup_logging, write_json
from src.visualization import generate_figures


logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    started_at = datetime.now(timezone.utc).isoformat()
    logger.info("AgentRadar-Stat pipeline started at %s", started_at)
    config = load_config()
    ensure_directories(config)
    warnings: list[str] = []

    print("[1/17] Collecting GitHub API data, with sample fallback if needed...")
    repos = collect_data(config)
    logger.info("Step 1 completed: collected %s repositories", len(repos))

    print("[2/17] Cleaning data...")
    cleaned = clean_data(config)
    logger.info("Step 2 completed: cleaned %s repositories", len(cleaned))

    print("[3/17] Building features...")
    featured = build_features(config)
    logger.info("Step 3 completed: feature table rows=%s", len(featured))

    print("[4/17] Scoring projects...")
    scored = score_projects(config)
    logger.info("Step 4 completed: scored rows=%s", len(scored))

    print("[5/17] Running statistical analysis...")
    stats = run_statistical_analysis(config)
    logger.info("Step 5 completed: sample_size=%s", stats.get("sample_size"))

    print("[6/17] Comparing clustering algorithms and assigning final clusters...")
    clustered = run_advanced_clustering(config)
    logger.info("Step 6 completed: clustered rows=%s", len(clustered))

    print("[7/17] Defining leakage-aware modeling labels...")
    labeled = define_model_tasks(config)
    logger.info("Step 7 completed: labels rows=%s", len(labeled))

    print("[8/17] Training sklearn model comparison and explanations...")
    model_metrics = train_models(config)
    logger.info("Step 8 completed: sklearn tasks=%s", list(model_metrics.keys()) if isinstance(model_metrics, dict) else "unknown")

    print("[9/17] Training PyTorch baseline MLP...")
    try:
        torch_mlp_metrics = train_torch_mlp(config)
    except Exception as exc:  # noqa: BLE001 - model failure must not block reporting.
        logger.warning("PyTorch MLP failed and pipeline will continue: %s", exc)
        torch_mlp_metrics = {"status": "failed", "reason": str(exc)}
        warnings.append(f"PyTorch baseline MLP failed: {exc}")

    print("[10/17] Training PyTorch TabularWideDeepNet...")
    try:
        torch_tabular_metrics = train_torch_tabular(config)
    except Exception as exc:  # noqa: BLE001
        logger.warning("PyTorch tabular model failed and pipeline will continue: %s", exc)
        torch_tabular_metrics = {"status": "failed", "reason": str(exc)}
        warnings.append(f"PyTorch TabularWideDeepNet failed: {exc}")

    print("[11/17] Generating personalized recommendation demo...")
    profile = default_user_profile()
    try:
        personalized = generate_personalized_recommendations(config, profile=profile)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Personalization failed and pipeline will continue: %s", exc)
        personalized = pd.DataFrame()
        warnings.append(f"Personalization failed: {exc}")

    print("[12/17] Running DeepSeek agents with generic and personalized context...")
    agent_outputs = run_agents(config)
    logger.info("Step 12 completed: agents=%s", len(agent_outputs))

    print("[13/17] Generating figures...")
    figures = generate_figures(config)

    print("[14/17] Generating HTML dashboard...")
    dashboard_path = generate_dashboard(config)
    logger.info("Step 13-14 completed: figures=%s dashboard=%s", len(figures), dashboard_path)

    print("[15/18] Generating HTML report with modeling and personalization sections...")
    report_path = generate_report(config)

    print("[16/18] Exporting final PDF report if renderer is available...")
    pdf_result = export_report_pdf(report_path)
    if not pdf_result.get("pdf_generated"):
        warnings.append(str(pdf_result.get("pdf_warning", "PDF export failed.")))

    print("[17/18] Writing final run summary...")
    finished_at = datetime.now(timezone.utc).isoformat()
    current = pd.read_csv(Path(config["paths"]["scored_repos"]))
    data_mode = "api_live" if (current["source_type"] == "api_live").any() else "sample_fallback"
    if data_mode == "sample_fallback":
        warnings.append("GitHub API unavailable or returned no usable rows; sample fallback used.")
    if torch_mlp_metrics.get("status") not in {"ok", None}:
        warnings.append(f"PyTorch MLP status: {torch_mlp_metrics.get('status')}")
    if torch_tabular_metrics.get("status") not in {"ok", None}:
        warnings.append(f"PyTorch tabular status: {torch_tabular_metrics.get('status')}")

    cluster_summary = _read_json("outputs/reports/cluster_stability.json")
    collection_log = _read_json(config["paths"].get("collection_log", "data/raw/api_collection_log.json"))
    cluster_comparison = _read_csv("outputs/reports/cluster_model_comparison.csv")
    best_cluster = cluster_comparison.sort_values("selection_score", ascending=False).iloc[0].to_dict() if not cluster_comparison.empty and "selection_score" in cluster_comparison else {}
    best_task_a = _best_model("outputs/reports/model_metrics_task_a.csv")
    best_task_b = _best_model("outputs/reports/model_metrics_task_b.csv")
    collection_fallback_used = bool(collection_log.get("fallback_used", data_mode == "sample_fallback"))
    agent_fallback_used = any(item.get("fallback_used") for item in agent_outputs.values())
    write_json(
        "outputs/reports/run_summary.json",
        {
            "started_at": started_at,
            "finished_at": finished_at,
            "data_mode": data_mode,
            "repo_count": int(len(current)),
            "source_type_counts": current["source_type"].value_counts().to_dict(),
            "requested_keywords": collection_log.get("requested_keywords", []),
            "search_strategies": collection_log.get("search_strategies", []),
            "per_keyword_limit": collection_log.get("per_keyword_limit"),
            "max_repos": collection_log.get("max_repos"),
            "raw_items_before_dedup": collection_log.get("raw_items_before_dedup"),
            "repos_after_dedup": collection_log.get("repos_after_dedup"),
            "repos_after_relevance_filter": collection_log.get("repos_after_relevance_filter"),
            "final_api_live_count": collection_log.get("final_api_live_count"),
            "seed_repos_requested": collection_log.get("seed_repos_requested", []),
            "seed_repos_success": collection_log.get("seed_repos_success", []),
            "seed_repos_failed": collection_log.get("seed_repos_failed", []),
            "fallback_reason": collection_log.get("fallback_reason", ""),
            "raw_data_path": config["paths"]["raw_repos"],
            "processed_data_path": config["paths"]["feature_repos"],
            "scored_data_path": config["paths"]["scored_repos"],
            "clustered_data_path": config["paths"].get("clustered_repos", "data/processed/clustered_repos.csv"),
            "best_cluster_model": best_cluster.get("model"),
            "best_k": best_cluster.get("k"),
            "cluster_stability": cluster_summary,
            "best_sklearn_model_task_a": best_task_a,
            "best_sklearn_model_task_b": best_task_b,
            "best_torch_model": torch_tabular_metrics.get("model_name") if torch_tabular_metrics.get("status") == "ok" else "torch_mlp_baseline",
            "personalization_demo_path": "outputs/reports/personalized_recommendations.csv" if not personalized.empty else None,
            "model_card_path": "outputs/reports/model_card.md",
            "torch_model_card_path": "outputs/reports/torch_model_card.md",
            "figure_count": len(figures),
            "agent_count": len(agent_outputs),
            "dashboard_path": dashboard_path,
            "report_path": report_path,
            "report_pdf_path": pdf_result.get("report_pdf_path"),
            "pdf_generated": bool(pdf_result.get("pdf_generated")),
            "pdf_warning": pdf_result.get("pdf_warning", ""),
            "agent_output_dir": config["paths"].get("agents_dir", "outputs/agents"),
            "fallback_used": collection_fallback_used,
            "collection_fallback_used": collection_fallback_used,
            "agent_fallback_used": bool(agent_fallback_used),
            "warnings": warnings,
        },
    )

    print("[18/18] Done. Outputs are under data/processed and outputs/.")
    logger.info("AgentRadar-Stat pipeline finished at %s", finished_at)


def _read_json(path: str) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _read_csv(path: str) -> pd.DataFrame:
    target = Path(path)
    return pd.read_csv(target) if target.exists() else pd.DataFrame()


def _best_model(path: str) -> dict[str, Any]:
    df = _read_csv(path)
    if df.empty or "f1" not in df.columns:
        return {}
    return df.sort_values("f1", ascending=False).iloc[0].to_dict()


if __name__ == "__main__":
    main()
