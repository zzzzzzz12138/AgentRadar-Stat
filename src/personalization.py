from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .user_profile import UserProfile, build_user_profile_from_dict


TOPIC_KEYWORDS = {
    "Coding Agent": ["code", "coding", "coder", "devin", "software", "program"],
    "RAG Agent": ["rag", "retrieval", "knowledge", "vector"],
    "MCP Tool": ["mcp", "tool", "server", "protocol"],
    "Workflow Agent": ["workflow", "flow", "automation", "orchestration"],
    "Research Agent": ["research", "paper", "scientific", "academic"],
    "Data Agent": ["data", "analytics", "sql", "database"],
    "Multimodal Agent": ["multimodal", "vision", "image", "audio"],
    "AutoML Agent": ["automl", "mlops", "model"],
    "Local LLM": ["local", "ollama", "llama", "gguf"],
    "Agent Framework": ["framework", "agent", "langchain", "autogen", "crew"],
}


def profile_to_weight_adjustments(profile: UserProfile | dict[str, Any]) -> dict[str, float]:
    """Map a user profile to interpretable recommendation weights."""
    if not isinstance(profile, UserProfile):
        profile = build_user_profile_from_dict(profile)
    weights = {
        "base_weight": 0.52,
        "preference_weight": 0.10,
        "feasibility_weight": 0.12,
        "goal_weight": 0.10,
        "language_weight": 0.07,
        "topic_weight": 0.07,
        "hardware_weight": 0.07,
        "risk_penalty_weight": 0.12,
    }
    role_goal = f"{profile.user_role} {profile.main_goal}"
    if "课程项目" in role_goal or "复现" in role_goal or "开发者" in role_goal:
        weights.update({"feasibility_weight": 0.18, "hardware_weight": 0.10, "risk_penalty_weight": 0.14, "base_weight": 0.45})
    if "社区观察" in role_goal or "趋势" in role_goal or "生态" in role_goal:
        weights.update({"goal_weight": 0.16, "base_weight": 0.56, "risk_penalty_weight": 0.08})
    if "维护者" in role_goal or "贡献" in role_goal:
        weights.update({"preference_weight": 0.13, "goal_weight": 0.15, "risk_penalty_weight": 0.10})
    if "研究" in role_goal or "科研" in role_goal:
        weights.update({"topic_weight": 0.12, "goal_weight": 0.14, "base_weight": 0.48})
    if profile.risk_preference == "低风险稳健":
        weights["risk_penalty_weight"] = max(weights["risk_penalty_weight"], 0.20)
    elif profile.risk_preference == "愿意尝试前沿高风险项目":
        weights["risk_penalty_weight"] = min(weights["risk_penalty_weight"], 0.06)
        weights["topic_weight"] += 0.03
    return weights


def compute_personalized_score(df: pd.DataFrame, profile: UserProfile | dict[str, Any]) -> pd.DataFrame:
    """Add personalized score and component columns to a scored repository table."""
    if not isinstance(profile, UserProfile):
        profile = build_user_profile_from_dict(profile)
    out = df.copy()
    weights = profile_to_weight_adjustments(profile)
    base = _norm(out.get("final_potential_score", pd.Series(0, index=out.index)))
    preference = _norm(out.get("documentation_score", 0)) * 0.45 + _norm(out.get("community_score", 0)) * 0.25 + _norm(out.get("activity_score", 0)) * 0.30
    feasibility = _norm(out.get("feasibility_score", 0)) * 0.7 + _norm(out.get("documentation_score", 0)) * 0.3
    goal = _goal_score(out, profile)
    language = _language_score(out, profile)
    topic = _topic_score(out, profile)
    hardware = _hardware_score(out, profile)
    risk = _norm(out.get("risk_score", 0))
    score = (
        base * weights["base_weight"]
        + preference * weights["preference_weight"]
        + feasibility * weights["feasibility_weight"]
        + goal * weights["goal_weight"]
        + language * weights["language_weight"]
        + topic * weights["topic_weight"]
        + hardware * weights["hardware_weight"]
        - risk * weights["risk_penalty_weight"]
    )
    out["base_score"] = (base * 100).round(3)
    out["preference_match_score"] = (preference * 100).round(3)
    out["feasibility_match_score"] = (feasibility * 100).round(3)
    out["goal_match_score"] = (goal * 100).round(3)
    out["language_match_score"] = (language * 100).round(3)
    out["topic_match_score"] = (topic * 100).round(3)
    out["hardware_match_score"] = (hardware * 100).round(3)
    out["personalized_risk_penalty"] = (risk * weights["risk_penalty_weight"] * 100).round(3)
    out["personalized_score"] = (np.clip(score, 0, 1) * 100).round(3)
    out["personalized_good_match_flag"] = (out["personalized_score"] >= out["personalized_score"].quantile(0.75)).astype(int) if len(out) else 0
    return out


def explain_personalized_match(row: pd.Series | dict[str, Any], profile: UserProfile | dict[str, Any]) -> dict[str, Any]:
    """Create a compact explanation grounded in scored fields and the user profile."""
    if not isinstance(profile, UserProfile):
        profile = build_user_profile_from_dict(profile)
    r = row if isinstance(row, pd.Series) else pd.Series(row)
    reasons = []
    warnings = []
    if float(r.get("language_match_score", 0)) >= 80:
        reasons.append(f"语言匹配：{r.get('language', 'unknown')} 符合偏好。")
    if float(r.get("topic_match_score", 0)) >= 60:
        reasons.append("主题匹配：项目名称、topics 或 README 与偏好方向接近。")
    if float(r.get("feasibility_match_score", 0)) >= 60:
        reasons.append("复现可行性较好：文档与可行性信号较强。")
    if float(r.get("hardware_match_score", 0)) >= 70:
        reasons.append(f"硬件适配：{profile.hardware_condition} 下更容易启动。")
    if not reasons:
        reasons.append("综合分数较高，但需要人工检查 README 与环境依赖。")
    if float(r.get("risk_score", 0)) >= 65:
        warnings.append("风险偏高：issue 压力、维护间隔或敏感依赖需要复核。")
    if profile.hardware_condition in {"CPU-only", "本地普通电脑"} and int(r.get("mentions_gpu", 0) or 0) > 0:
        warnings.append("README 出现 GPU 相关信号，本地普通电脑用户需先确认是否有轻量 demo。")
    if float(r.get("days_since_update", 0) or 0) > 180:
        warnings.append("近期维护不足，建议检查最近 commit 和 issue 回复。")
    action = _recommended_action(profile)
    full_name = str(r.get("full_name", "该项目"))
    return {
        "full_name": full_name,
        "personalized_score": float(r.get("personalized_score", 0)),
        "base_score": float(r.get("base_score", r.get("final_potential_score", 0))),
        "match_reasons": reasons,
        "risk_warnings": warnings or ["未发现明显高风险信号，但仍需检查许可证和运行环境。"],
        "recommended_action": action,
        "three_day_plan": [
            f"Day 1: 阅读 {full_name} 的 README、安装说明和示例，确认 Python/Node/硬件要求。",
            "Day 2: 跑通最小 demo，记录依赖、报错、数据输入与输出截图。",
            "Day 3: 做一个小改造或对比实验，整理复现路线、风险和 Codex 任务清单。",
        ],
        "codex_prompt": f"请作为 Python/软件工程助教，帮我复现 GitHub 项目 {full_name}：先梳理依赖和最小运行路径，再生成适合 Windows 11 本地普通电脑的三天复现计划，并标出可能失败的步骤。",
    }


def _norm(value: Any) -> pd.Series:
    s = pd.Series(value).astype(float) if not isinstance(value, pd.Series) else pd.to_numeric(value, errors="coerce").fillna(0)
    if len(s) == 0:
        return s
    lo, hi = float(s.min()), float(s.max())
    if hi == lo:
        return pd.Series(0.5, index=s.index)
    return ((s - lo) / (hi - lo)).clip(0, 1)


def _language_score(df: pd.DataFrame, profile: UserProfile) -> pd.Series:
    if "无明显偏好" in profile.preferred_languages:
        return pd.Series(0.7, index=df.index)
    lang = df.get("language", pd.Series("", index=df.index)).fillna("").str.lower()
    prefs = {item.lower().replace("c++", "c++") for item in profile.preferred_languages}
    return lang.isin(prefs).astype(float)


def _topic_score(df: pd.DataFrame, profile: UserProfile) -> pd.Series:
    text = (
        df.get("full_name", pd.Series("", index=df.index)).fillna("")
        + " "
        + df.get("description", pd.Series("", index=df.index)).fillna("")
        + " "
        + df.get("topic_label", pd.Series("", index=df.index)).fillna("")
        + " "
        + df.get("cluster_name", pd.Series("", index=df.index)).fillna("")
    ).str.lower()
    score = pd.Series(0.0, index=df.index)
    for topic in profile.preferred_topics:
        keywords = TOPIC_KEYWORDS.get(topic, [topic.lower()])
        score += text.apply(lambda value: any(keyword.lower() in value for keyword in keywords)).astype(float)
    return (score / max(1, len(profile.preferred_topics))).clip(0, 1)


def _hardware_score(df: pd.DataFrame, profile: UserProfile) -> pd.Series:
    cpu = pd.to_numeric(df.get("mentions_cpu", pd.Series(0, index=df.index)), errors="coerce").fillna(0)
    gpu = pd.to_numeric(df.get("mentions_gpu", pd.Series(0, index=df.index)), errors="coerce").fillna(0)
    feasible = _norm(df.get("feasibility_score", pd.Series(0, index=df.index)))
    if profile.hardware_condition in {"CPU-only", "本地普通电脑"}:
        return (0.55 * feasible + 0.25 * (cpu > 0).astype(float) + 0.20 * (gpu == 0).astype(float)).clip(0, 1)
    if profile.hardware_condition in {"有普通 GPU", "有较强 GPU", "有独立显卡", "云端资源可用"}:
        return (0.6 * feasible + 0.25 * (gpu >= 0).astype(float) + 0.15 * _norm(df.get("innovation_score", 0))).clip(0, 1)
    return feasible


def _goal_score(df: pd.DataFrame, profile: UserProfile) -> pd.Series:
    goal = profile.main_goal
    if "趋势" in goal or "生态" in goal:
        return (_norm(df.get("trend_score", 0)) * 0.6 + _norm(df.get("community_score", 0)) * 0.4).clip(0, 1)
    if "贡献" in goal:
        issues = _norm(df.get("open_issues_count", 0))
        return (_norm(df.get("community_score", 0)) * 0.45 + _norm(df.get("activity_score", 0)) * 0.35 + issues * 0.20).clip(0, 1)
    if "科研" in goal or "研究" in profile.user_role:
        cluster = df.get("cluster_label", pd.Series(0, index=df.index)).astype(str)
        rarity = 1 - cluster.map(cluster.value_counts(normalize=True)).fillna(0.5)
        return (_norm(df.get("innovation_score", 0)) * 0.65 + _norm(rarity) * 0.35).clip(0, 1)
    return (_norm(df.get("feasibility_score", 0)) * 0.5 + _norm(df.get("documentation_score", 0)) * 0.5).clip(0, 1)


def _recommended_action(profile: UserProfile) -> str:
    if "Codex Prompt" in " ".join(profile.output_preference):
        return "生成 Codex 复现与二次开发任务，先跑通最小 demo。"
    if "研究" in profile.main_goal or "科研" in profile.main_goal:
        return "整理研究问题、技术路线和可扩展实验。"
    if "贡献" in profile.main_goal:
        return "优先阅读 issue 与 contributing，寻找文档修复或小功能切入点。"
    return "按三天复现路线推进，并保留环境、报错和截图证据。"
