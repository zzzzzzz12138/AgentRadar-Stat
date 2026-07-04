from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .utils import project_path


AGENT_NAME_CN = {
    "CollectorAgent": "采集策略智能体",
    "DataQualityAgent": "数据质量诊断智能体",
    "TopicAgent": "主题识别智能体",
    "ScoringAgent": "评分解释智能体",
    "ProjectAdvisorAgent": "个性化项目顾问智能体",
    "ReportAgent": "报告生成智能体",
    "CriticAgent": "事实审查智能体",
}

AGENT_ROLE_CN = {
    "CollectorAgent": "检查关键词、seed 仓库、多排序策略和采集覆盖边界。",
    "DataQualityAgent": "诊断数据来源、README 完整度、缺失值和建模准备度。",
    "TopicAgent": "把仓库文本信号归纳为 Coding Agent、RAG、MCP、Workflow 等主题。",
    "ScoringAgent": "解释综合潜力分、风险分、推荐等级和画像匹配差异。",
    "ProjectAdvisorAgent": "结合用户画像输出项目选择、复现路线和 Codex Prompt。",
    "ReportAgent": "把数据、模型、聚类、推荐和局限组织成项目报告叙事。",
    "CriticAgent": "审查结论是否绑定到字段、图表、模型指标和输出文件。",
}


def load_agent_records(agent_dir: str = "outputs/agents") -> list[dict[str, Any]]:
    """Load Agent output files and normalize them for UI/report display."""
    records = []
    for path in sorted(project_path(agent_dir).glob("*Agent.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        records.append(normalize_agent_record(raw, path))
    return records


def normalize_agent_record(raw: dict[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    """Normalize JSON, dict, or text-like Agent output into display fields."""
    agent_name = raw.get("agent_name") or (Path(path).stem if path else "Agent")
    content = raw.get("agent_output") or raw.get("content") or ""
    parsed = _parse_content(content)
    status = parsed.get("status") or ("warning" if raw.get("fallback_used") else "pass")
    normalized = {
        "title": agent_name,
        "title_cn": AGENT_NAME_CN.get(agent_name, agent_name),
        "role_cn": AGENT_ROLE_CN.get(agent_name, "将数据证据转写为可讲解的解释内容。"),
        "status": status,
        "summary": _clean_text(parsed.get("summary") or _first_sentence(content) or f"{AGENT_NAME_CN.get(agent_name, agent_name)}已生成解释。"),
        "key_findings": _clean_items(_listify(parsed.get("key_findings")) or _fallback_findings(content)),
        "evidence": _clean_items(_listify(parsed.get("evidence")) or raw.get("evidence_fields", [])),
        "risks": _clean_items(_listify(parsed.get("risks"))),
        "recommendations": _clean_items(_listify(parsed.get("recommendations"))),
        "next_steps": _clean_items(_listify(parsed.get("next_steps"))),
        "codex_prompt": parsed.get("codex_prompt") or _extract_codex_prompt(content),
        "fallback_used": bool(raw.get("fallback_used")),
        "model": raw.get("model") or raw.get("model_name") or "deepseek-v4-pro",
        "created_at": raw.get("created_at"),
        "output_path": raw.get("output_path") or str(path or ""),
        "raw": raw,
    }
    if agent_name == "CriticAgent":
        normalized.update(
            {
                "weak_sentences": _listify(parsed.get("weak_sentences")) or _extract_bullets(content),
                "evidence_gaps": _listify(parsed.get("evidence_gaps")) or _listify(parsed.get("missing_evidence")),
                "suggestions": _listify(parsed.get("suggestions")) or normalized["recommendations"],
                "final_verdict": parsed.get("final_verdict") or normalized["summary"],
            }
        )
    if agent_name == "ProjectAdvisorAgent":
        normalized.update(
            {
                "profile_summary": parsed.get("profile_summary") or _profile_summary_from_raw(raw),
                "recommendation_logic": parsed.get("recommendation_logic") or normalized["summary"],
                "top_projects": _listify(parsed.get("top_projects")) or _listify(parsed.get("recommended_projects")) or normalized["key_findings"],
                "not_recommended_even_if_popular": _listify(parsed.get("not_recommended_even_if_popular")),
                "recommended_projects": _listify(parsed.get("recommended_projects")) or _listify(parsed.get("top_projects")) or normalized["key_findings"],
                "difficulty": parsed.get("difficulty") or "medium",
                "three_day_plan": _listify(parsed.get("three_day_plan")) or normalized["next_steps"],
            }
        )
    return normalized


def load_single_project_cache(full_name: str, agent_name: str = "ScoringAgent") -> dict[str, Any] | None:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", full_name)
    path = project_path(f"outputs/agents/cache/{agent_name}_{safe}.json")
    if not path.exists():
        return None
    try:
        return normalize_agent_record(json.loads(path.read_text(encoding="utf-8")), path)
    except Exception:  # noqa: BLE001
        return None


def save_single_project_cache(full_name: str, agent_name: str, record: dict[str, Any]) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", full_name)
    path = project_path(f"outputs/agents/cache/{agent_name}_{safe}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def _parse_content(content: str) -> dict[str, Any]:
    text = str(content).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip().strip("`")
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _first_sentence(text: str) -> str:
    return str(text).strip().split("\n")[0][:240]


def _fallback_findings(text: str) -> list[dict[str, str]]:
    bullets = _extract_bullets(text)
    if bullets:
        return [{"finding": item, "evidence": "Agent 输出摘要"} for item in bullets[:5]]
    return [{"finding": _first_sentence(text), "evidence": "Agent 输出摘要"}] if text else []


def _extract_bullets(text: str) -> list[str]:
    lines = [line.strip(" -•\t") for line in str(text).splitlines()]
    return [line for line in lines if len(line) > 8][:8]


def _extract_codex_prompt(text: str) -> str:
    marker = "Codex"
    if marker in str(text):
        return str(text)[str(text).find(marker) :][:1200]
    return ""


def _profile_summary_from_raw(raw: dict[str, Any]) -> str:
    profile = raw.get("input_summary", {}).get("user_profile", {})
    if not isinstance(profile, dict) or not profile:
        return ""
    return " / ".join(str(profile.get(key, "")) for key in ["user_role", "main_goal", "hardware_condition", "risk_preference"] if profile.get(key))


def _clean_items(values: list[Any]) -> list[Any]:
    return [_clean_dict_or_text(item) for item in values if _clean_dict_or_text(item)]


def _clean_dict_or_text(item: Any) -> Any:
    if isinstance(item, dict):
        cleaned = {key: _clean_text(value) for key, value in item.items() if _clean_text(value)}
        return cleaned
    return _clean_text(item)


def _clean_text(value: Any) -> str:
    text = str(value or "").strip()
    banned = [
        "fallback based on real fields:",
        "fallback based on real fields",
        "sample_fallback",
        "sample fallback",
        "api_live",
        "CPU-only",
        "CPU only",
        "答辩讲法",
        "答辩",
        "生成时间",
        "最近更新",
        "recommendation_level",
        "final_potential_score",
        "personalized_score",
        "risk_score",
        "stars_total",
        "forks_total",
        "risk_level_cn",
        "cluster_name",
        "pca_x",
        "pca_y",
        "task_b_proxy_good_project",
        "calibrated_random_forest",
        "agent_relevance_score",
        "has_demo",
        "has_requirements",
        "embedding",
        "wide",
        "api_status",
        "readme_fetch_status",
        "source_type",
        "user_profile",
        "fallback shown",
        "generated explanation",
        "value hidden",
        "configured",
        "Data mode",
        "Rate limit not collected",
        "JSON",
        "dict",
        "Agent text summary",
        "未显式给出",
        "explanation generated",
    ]
    for phrase in banned:
        text = text.replace(phrase, "")
    text = re.sub(r"\b(finding|evidence|risk|action)\s*:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"(^|[；，。])\s*(is|=|:|：)\s*([；，。]|$)", r"\1", text, flags=re.IGNORECASE)
    text = text.strip(" -:;，。")
    return text
