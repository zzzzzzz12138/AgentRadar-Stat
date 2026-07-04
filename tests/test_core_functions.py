from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.agent_display import normalize_agent_record
from src.clustering import add_cluster_fields
from src.clustering_advanced import compare_cluster_models, run_advanced_clustering
from src.feature_engineering import add_features
from src.model_tasks import NO_LEAKAGE_FEATURES, define_model_tasks
from src.modeling import train_models
from src.personalization import compute_personalized_score, profile_to_weight_adjustments
from src.recommendation_engine import generate_personalized_recommendations
from src.report_generator import generate_report
from src.sample_data import ensure_sample_data
from src.scoring import add_scores
from src.torch_tabular import train_torch_tabular
from src.user_profile import UserProfile


def _sample_scored(tmp_path: Path, rows: int = 150) -> tuple[pd.DataFrame, dict]:
    sample_path = ensure_sample_data(tmp_path / "sample.csv", rows=rows)
    df = add_cluster_fields(add_scores(add_features(pd.read_csv(sample_path))))
    paths = {
        "scored_repos": str(tmp_path / "scored.csv"),
        "clustered_repos": str(tmp_path / "clustered.csv"),
        "raw_repos": str(tmp_path / "raw.csv"),
        "feature_repos": str(tmp_path / "feature.csv"),
    }
    df.to_csv(paths["scored_repos"], index=False)
    return df, {"paths": paths, "modeling": {"test_size": 0.25, "random_state": 42, "torch_epochs": 2}}


def test_sample_data_has_required_rows(tmp_path):
    path = ensure_sample_data(tmp_path / "sample.csv", rows=150)
    df = pd.read_csv(path)
    assert len(df) >= 150
    assert {"full_name", "readme_text", "source_type", "api_status"}.issubset(df.columns)
    assert set(df["source_type"]) == {"sample_fallback"}


def test_feature_and_scoring_columns():
    base = pd.DataFrame([
        {"repo_name": "agent-demo", "description": "RAG coding agent", "topics": "rag|agent", "readme_text": "Install quickstart demo example requirements CPU docker", "created_at": "2024-01-01T00:00:00Z", "pushed_at": "2026-01-01T00:00:00Z", "stars_total": 100, "forks_total": 20, "watchers_total": 50, "open_issues_count": 5, "stars_this_week": 10},
        {"repo_name": "old-gpu", "description": "experimental agent", "topics": "agent", "readme_text": "Requires GPU and API key", "created_at": "2020-01-01T00:00:00Z", "pushed_at": "2020-01-01T00:00:00Z", "stars_total": 10, "forks_total": 1, "watchers_total": 3, "open_issues_count": 20, "stars_this_week": 0},
    ])
    featured = add_features(base)
    scored = add_scores(featured)
    assert "agent_relevance_score" in featured.columns
    assert "final_potential_score" in scored.columns
    assert set(scored["recommendation_level"].astype(str)).issubset({"A", "B", "C", "D"})


def test_user_profile_and_personalized_score(tmp_path):
    df, config = _sample_scored(tmp_path)
    profile = UserProfile(main_goal="选择可复现项目", hardware_condition="CPU-only")
    weights = profile_to_weight_adjustments(profile)
    scored = compute_personalized_score(df, profile)
    recommendations = generate_personalized_recommendations(config, profile=profile, top_n=10)
    assert weights["base_weight"] > 0
    assert "personalized_score" in scored.columns
    assert not recommendations.empty


def test_label_report_and_no_leakage_features(tmp_path):
    _, config = _sample_scored(tmp_path)
    labeled = define_model_tasks(config)
    assert {"task_a_high_potential", "task_b_proxy_good_project"}.issubset(labeled.columns)
    assert "final_potential_score" not in NO_LEAKAGE_FEATURES
    assert "recommendation_level" not in NO_LEAKAGE_FEATURES
    assert "risk_score" not in NO_LEAKAGE_FEATURES
    assert Path("outputs/reports/label_definition_report.md").exists()


def test_advanced_clustering_comparison_and_profile(tmp_path):
    df, config = _sample_scored(tmp_path)
    numeric = df[["stars_total", "forks_total", "open_issues_count", "readme_length", "topic_count"]].fillna(0).to_numpy()
    comparison = compare_cluster_models(numeric)
    clustered = run_advanced_clustering(config)
    assert "selection_score" in comparison.columns
    assert {"cluster_label", "cluster_name", "pca_x", "pca_y"}.issubset(clustered.columns)
    assert Path("outputs/reports/cluster_model_comparison.csv").exists()


def test_model_cards_and_report_generated_from_sample(tmp_path):
    _, config = _sample_scored(tmp_path)
    define_model_tasks(config)
    metrics = train_models(config)
    torch_result = train_torch_tabular(config)
    report_path = generate_report(config)
    assert "task_a" in metrics and "task_b" in metrics
    assert Path("outputs/reports/model_card.md").exists()
    assert Path("outputs/reports/torch_model_card.md").exists()
    assert torch_result.get("status") in {"ok", "skipped"}
    assert report_path.endswith("agent_radar_report.html")
    report_text = Path(report_path).read_text(encoding="utf-8")
    assert "各聚类类型代表项目" in report_text
    assert "任务 A 特征重要性" in report_text
    assert "任务 B 特征重要性" in report_text
    assert "agent_radar_report.pdf" in report_text
    for token in ["source_type", "user_profile", "risk_score", "final_potential_score", "personalized_score"]:
        assert token not in report_text


def test_env_file_is_not_scanned_or_written_to_outputs():
    forbidden = ["DEEPSEEK_API_KEY=", "GITHUB_TOKEN="]
    output_files = [
        "outputs/reports/agent_radar_report.html",
        "outputs/reports/stat_summary.json",
        "outputs/reports/run_summary.json",
        "outputs/reports/personalization_rules.md",
    ]
    for path in output_files:
        try:
            text = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            continue
        for item in forbidden:
            assert item not in text


def test_agent_display_removes_internal_field_traces():
    record = normalize_agent_record(
        {
            "agent_name": "DataQualityAgent",
            "agent_output": '{"summary":"source_type api_live user_profile configured","key_findings":["readme_fetch_status fallback shown"],"risks":["generated explanation"]}',
        }
    )
    visible = " ".join(
        [record.get("role_cn", ""), record.get("summary", "")]
        + [str(item) for key in ["key_findings", "evidence", "risks", "recommendations", "next_steps"] for item in record.get(key, [])]
    )
    for token in ["source_type", "user_profile", "api_live", "readme_fetch_status", "fallback shown", "generated explanation", "configured"]:
        assert token not in visible
