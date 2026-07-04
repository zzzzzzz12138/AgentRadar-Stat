from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .deepseek_client import DeepSeekClient
from .user_profile import default_user_profile
from .utils import project_path


BASE_JSON_CONTRACT = """
Return valid compact JSON only. Use this schema:
{
  "status": "pass|warning|fail",
  "summary": "one sentence",
  "key_findings": [{"finding": "...", "evidence": "..."}],
  "risks": [{"risk": "...", "severity": "low|medium|high", "evidence": "..."}],
  "recommendations": [{"action": "...", "reason": "..."}],
  "next_steps": ["..."],
  "codex_prompt": "optional prompt"
}
Do not include secrets, tokens, API keys, or raw request payloads.
"""


SYSTEM_PROMPTS = {
    "CollectorAgent": "You are CollectorAgent. Focus on collection keyword strategy, GitHub API scope, representativeness risks, rate limit risks, and missing keyword suggestions. " + BASE_JSON_CONTRACT,
    "DataQualityAgent": "You are DataQualityAgent. Audit sample_size, source_type distribution, API success ratio, README status, missing-value risks, outliers, and modeling readiness. Cite field names as evidence. " + BASE_JSON_CONTRACT,
    "TopicAgent": "You are TopicAgent. Classify visible projects into Coding Agent, RAG Agent, Research Agent, Workflow Agent, MCP Tool, Multimodal Agent, AutoML Agent, or Data Agent. Explain evidence and ambiguity. " + BASE_JSON_CONTRACT,
    "ScoringAgent": "You are ScoringAgent. Explain recommendation_level, final_potential_score, component scores, personalized_score, user_profile fit, and risk warnings. Distinguish generic ranking from personalized ranking. " + BASE_JSON_CONTRACT,
    "ProjectAdvisorAgent": "You are ProjectAdvisorAgent. Use user_profile and personalized_top_projects. Explain why projects fit this user, which popular projects are not suitable, risks, learning/reproduction route, and Codex prompts. " + BASE_JSON_CONTRACT,
    "ReportAgent": "You are ReportAgent. Summarize overall findings, data evidence, model evidence, cluster evidence, personalization evidence, and limitations. Avoid unsupported claims. " + BASE_JSON_CONTRACT,
    "CriticAgent": "You are CriticAgent. Add weak_sentences: [{sentence, problem, needed_evidence}], suggestions: [], final_verdict. Return pass/warning/fail based on evidence binding. " + BASE_JSON_CONTRACT,
}


def run_agents(config: dict[str, Any]) -> dict[str, Any]:
    """Run the seven DeepSeek-backed agents, falling back to deterministic templates."""
    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    top = df.sort_values("final_potential_score", ascending=False).head(int(config.get("collection", {}).get("max_agent_repos", 30)))
    client = DeepSeekClient(
        base_url=config.get("deepseek", {}).get("base_url", "https://api.deepseek.com"),
        model=config.get("deepseek", {}).get("model", "deepseek-v4-pro"),
    )
    use_agents = bool(config.get("deepseek", {}).get("use_agents", True))
    summary = _data_summary(df, top, config)
    outputs: dict[str, Any] = {}
    for agent_name, system_prompt in SYSTEM_PROMPTS.items():
        fallback_text = _fallback_agent_text(agent_name, summary)
        if not use_agents:
            result = {"content": fallback_text, "api_call_status": "disabled_by_config", "fallback_used": True, "model": client.model}
        else:
            result = client.chat_completion(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(summary, ensure_ascii=False)}],
                temperature=config.get("deepseek", {}).get("temperature", 0.2),
                max_tokens=config.get("deepseek", {}).get("max_tokens", 900),
                timeout=config.get("deepseek", {}).get("timeout", 45),
                fallback_message=fallback_text,
            )
        record = {
            "agent_name": agent_name,
            "model": result.get("model"),
            "model_name": result.get("model"),
            "prompt_version": "stage3_personalization",
            "input_summary": summary,
            "agent_output": result.get("content", ""),
            "evidence_fields": [
                "source_type",
                "api_status",
                "readme_fetch_status",
                "final_potential_score",
                "recommendation_level",
                "personalized_score",
                "risk_score",
                "cluster_name",
                "user_profile",
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "api_call_status": result.get("api_call_status"),
            "fallback_used": result.get("fallback_used"),
        }
        outputs[agent_name] = record
        path = project_path(f"outputs/agents/{agent_name}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        record["output_path"] = str(path)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return outputs


def _data_summary(df: pd.DataFrame, top: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    readme_status = df["readme_fetch_status"].value_counts().to_dict() if "readme_fetch_status" in df.columns else {}
    api_live_ratio = float((df["source_type"] == "api_live").mean()) if len(df) else 0.0
    missing = df.isna().mean().sort_values(ascending=False).head(8).round(3).to_dict()
    cluster_counts = df["cluster_name"].value_counts().to_dict() if "cluster_name" in df.columns else {}
    profile = default_user_profile()
    personalized_path = project_path("outputs/reports/personalized_recommendations.csv")
    personalized_top = []
    if personalized_path.exists():
        personalized_df = pd.read_csv(personalized_path)
        personalized_top = personalized_df.head(8).to_dict("records")
    return {
        "sample_size": int(len(df)),
        "keywords": config.get("collection", {}).get("keywords", []),
        "user_profile": profile.to_dict(),
        "personalized_top_projects": personalized_top,
        "source_type_counts": df["source_type"].value_counts().to_dict(),
        "api_success_rate": api_live_ratio,
        "api_status_counts": df["api_status"].value_counts().head(10).to_dict(),
        "readme_status_counts": readme_status,
        "readme_success_rate": float((df.get("readme_fetch_status", pd.Series(index=df.index, dtype=object)) == "ok").mean()) if len(df) else 0.0,
        "missing_value_rate_top": missing,
        "cluster_counts": cluster_counts,
        "top_projects": top[[col for col in ["full_name", "language", "stars_total", "final_potential_score", "recommendation_level", "trend_score", "activity_score", "community_score", "documentation_score", "innovation_score", "feasibility_score", "risk_score", "personalized_score", "mentions_cpu", "mentions_api_key", "cluster_name"] if col in top.columns]].head(8).to_dict("records"),
        "high_risk_projects": df.sort_values("risk_score", ascending=False)[["full_name", "risk_score", "open_issues_count", "days_since_update"]].head(5).to_dict("records"),
    }


def _fallback_agent_text(agent_name: str, summary: dict[str, Any]) -> str:
    top_names = [item.get("full_name") for item in summary.get("top_projects", [])[:5]]
    personalized = summary.get("personalized_top_projects", [])[:5]
    profile = summary.get("user_profile", {})
    common = {
        "status": "warning",
        "summary": "",
        "key_findings": [
            {"finding": f"本轮报告基于 {summary.get('sample_size', 0)} 个仓库样本生成。", "evidence": f"source_type 分布：{summary.get('source_type_counts')}"},
            {"finding": f"优先展示项目包括：{'、'.join([str(x) for x in top_names[:3]])}。", "evidence": "top_projects、final_potential_score、recommendation_level"},
            {"finding": "所有解释结论需要回到表格字段、图表和模型指标验证。", "evidence": "final_potential_score、risk_score、cluster_name、model_metrics"},
        ],
        "risks": [
            {"risk": "GitHub 数据具有采集时点性，Star、Fork 和 Issue 会持续变化。", "severity": "medium", "evidence": "collected_at、updated_at"},
            {"risk": "README 与 topics 属于文本信号，可能存在命名风格造成的误判。", "severity": "medium", "evidence": "readme_fetch_status、topics"},
        ],
        "recommendations": [
            {"action": "展示时先讲数据规模，再讲评分、聚类、模型和推荐闭环。", "reason": "能够把工程量和方法严谨性串起来。"},
            {"action": "展示单个项目时同时说明潜力分、风险分和项目类型。", "reason": "避免把推荐简化成 Stars 排名。"},
        ],
        "next_steps": ["复核 Top 项目的 README 可复现性。", "把高风险项目作为反例说明评分体系边界。"],
        "codex_prompt": "请基于仓库字段、评分结果和用户画像，生成三天复现计划、风险清单与项目讲解要点。",
    }
    if agent_name == "CollectorAgent":
        common["summary"] = f"采集策略覆盖 {len(summary.get('keywords', []))} 个关键词方向，适合支撑 AI Agent 生态观察。"
        common["key_findings"].append({"finding": "关键词、seed 仓库和多排序策略共同扩大了样本覆盖。", "evidence": "keywords、source_type_counts、sample_size"})
    elif agent_name == "DataQualityAgent":
        common["summary"] = f"样本量为 {summary['sample_size']}，API 数据占比 {summary.get('api_success_rate', 0):.2%}，可以继续建模但要说明数据时点局限。"
        common["key_findings"].append({"finding": f"README 状态分布为 {summary.get('readme_status_counts')}。", "evidence": "readme_status_counts"})
    elif agent_name == "TopicAgent":
        common["summary"] = "主题识别主要依赖仓库名、description、topics、README 派生字段和聚类画像。"
        common["key_findings"].append({"finding": "Coding Agent、RAG、MCP、多智能体和工作流方向是报告中的核心主题。", "evidence": "topics、description、cluster_name"})
    elif agent_name == "ScoringAgent":
        common["summary"] = "评分解释应同时覆盖通用潜力、风险惩罚和个性化画像匹配，不能只讲热度。"
        common["key_findings"].append({"finding": "通用榜与个性化榜可能不同，说明推荐目标发生了变化。", "evidence": "final_potential_score、personalized_score"})
    elif agent_name == "ProjectAdvisorAgent":
        common["summary"] = "当前画像更适合选择文档清晰、Python 友好且风险可控的项目。"
        common["profile_summary"] = " / ".join(str(profile.get(k, "")) for k in ["user_role", "main_goal", "hardware_condition", "risk_preference"] if profile.get(k))
        common["top_projects"] = [{"full_name": p.get("full_name"), "reason": p.get("match_reasons", "画像匹配度较高")} for p in personalized[:5]]
        common["not_recommended_even_if_popular"] = summary.get("high_risk_projects", [])[:3]
        common["three_day_plan"] = ["第 1 天：阅读 README、跑通安装和最小 demo。", "第 2 天：整理核心模块与输入输出，补一张流程图。", "第 3 天：完成复现实验、风险说明和展示脚本。"]
        common["codex_prompt"] = "请基于我选择的 GitHub 仓库，生成 Windows 11、Python 3.10 条件下的三天复现路线、依赖清单、演示脚本和风险提示。"
    elif agent_name == "ReportAgent":
        common["summary"] = "报告叙事应按数据采集、评分体系、聚类画像、模型预测、个性化推荐和 Agent 审查展开。"
        common["key_findings"].append({"finding": f"聚类画像分布为 {summary.get('cluster_counts')}。", "evidence": "cluster_counts"})
    else:
        common["summary"] = "报告整体可信，但展示时必须把结论绑定到数据字段、图表、模型指标和输出文件。"
        common["weak_sentences"] = [
            {"sentence": "模型能够预测项目未来成功。", "problem": "当前是代理标签建模，不是未来商业成功预测。", "needed_evidence": "Task A/B 定义和模型卡"},
            {"sentence": "Agent 结论就是事实。", "problem": "Agent 是解释层，不是事实来源。", "needed_evidence": "字段、图表、模型指标"},
        ]
        common["suggestions"] = [
            "展示中避免夸大预测能力。",
            "说明 GitHub 数据的采集时点性和 README 文本信号局限。",
        ]
        common["final_verdict"] = "可用于课程项目展示；关键结论已具备数据和模型证据，但应保留边界说明。"
    return json.dumps(common, ensure_ascii=False)
