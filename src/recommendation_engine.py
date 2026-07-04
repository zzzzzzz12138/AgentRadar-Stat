from __future__ import annotations

import json
from typing import Any

import pandas as pd

from .personalization import compute_personalized_score, explain_personalized_match, profile_to_weight_adjustments
from .user_profile import UserProfile, default_user_profile
from .utils import project_path


def generate_personalized_recommendations(
    config: dict[str, Any],
    profile: UserProfile | dict[str, Any] | None = None,
    top_n: int = 20,
) -> pd.DataFrame:
    """Generate personalized repository recommendations and persist auditable outputs."""
    profile = profile or default_user_profile()
    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    scored = compute_personalized_score(df, profile)
    ranked = scored.sort_values("personalized_score", ascending=False).head(top_n).copy()
    explanations = [explain_personalized_match(row, profile) for _, row in ranked.iterrows()]
    ranked["match_reasons"] = [json.dumps(item["match_reasons"], ensure_ascii=False) for item in explanations]
    ranked["risk_warnings"] = [json.dumps(item["risk_warnings"], ensure_ascii=False) for item in explanations]
    ranked["recommended_action"] = [item["recommended_action"] for item in explanations]
    ranked["three_day_plan"] = [json.dumps(item["three_day_plan"], ensure_ascii=False) for item in explanations]
    ranked["codex_prompt"] = [item["codex_prompt"] for item in explanations]

    out_csv = project_path("outputs/reports/personalized_recommendations.csv")
    out_json = project_path("outputs/reports/personalized_recommendations.json")
    out_md = project_path("outputs/reports/personalization_rules.md")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        col
        for col in [
            "full_name",
            "html_url",
            "language",
            "recommendation_level",
            "final_potential_score",
            "base_score",
            "personalized_score",
            "preference_match_score",
            "feasibility_match_score",
            "goal_match_score",
            "language_match_score",
            "topic_match_score",
            "hardware_match_score",
            "personalized_risk_penalty",
            "risk_score",
            "cluster_name",
            "match_reasons",
            "risk_warnings",
            "recommended_action",
            "three_day_plan",
            "codex_prompt",
        ]
        if col in ranked.columns
    ]
    ranked[columns].to_csv(out_csv, index=False, encoding="utf-8-sig")
    payload = {
        "profile": profile.to_dict() if isinstance(profile, UserProfile) else profile,
        "weights": profile_to_weight_adjustments(profile),
        "top_projects": [explain_personalized_match(row, profile) for _, row in ranked.head(10).iterrows()],
        "not_recommended_even_if_popular": _not_recommended(scored),
        "output_path": str(out_csv),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(_rules_markdown(profile, payload["weights"]), encoding="utf-8")
    scored.to_csv(project_path(config["paths"]["scored_repos"]), index=False, encoding="utf-8-sig")
    return ranked[columns]


def _not_recommended(df: pd.DataFrame) -> list[dict[str, str]]:
    if "final_potential_score" not in df or "personalized_score" not in df:
        return []
    popular = df.sort_values("final_potential_score", ascending=False).head(25).copy()
    popular["gap"] = popular["final_potential_score"] - popular["personalized_score"]
    rows = popular.sort_values("gap", ascending=False).head(5)
    result = []
    for _, row in rows.iterrows():
        reason = "通用评分高，但个性化匹配较低。"
        if float(row.get("risk_score", 0)) >= 65:
            reason += " 风险分偏高。"
        if float(row.get("hardware_match_score", 100)) < 40:
            reason += " 硬件条件匹配不足。"
        if float(row.get("language_match_score", 100)) < 40:
            reason += " 语言偏好不匹配。"
        result.append({"full_name": str(row.get("full_name")), "reason": reason})
    return result


def _rules_markdown(profile: UserProfile | dict[str, Any], weights: dict[str, float]) -> str:
    profile_dict = profile.to_dict() if isinstance(profile, UserProfile) else profile
    lines = [
        "# Personalization Rules",
        "",
        "本文件说明 AgentRadar-Stat 如何将通用评分转为用户画像下的个性化推荐分。",
        "",
        "## User Profile",
    ]
    lines.extend(f"- {key}: {value}" for key, value in profile_dict.items())
    lines.extend(
        [
            "",
            "## Scoring Formula",
            "",
            "`personalized_score = base_score * base_weight + preference + feasibility + goal + language + topic + hardware - risk_penalty`",
            "",
            "## Active Weights",
        ]
    )
    lines.extend(f"- {key}: {value:.3f}" for key, value in weights.items())
    lines.extend(
        [
            "",
            "## Leakage Control",
            "",
            "- 个性化推荐是在评分结果之上做排序适配，不把用户画像字段写入监督训练标签。",
            "- 监督模型仍使用 no_leakage_features，避免直接使用 final_potential_score 和子评分字段预测评分标签。",
            "- DeepSeek Agent 的个性化解释只作为说明层，不替代真实字段和模型指标。",
        ]
    )
    return "\n".join(lines) + "\n"
