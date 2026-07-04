from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .github_client import GitHubClient
from .sample_data import ensure_sample_data
from .utils import project_path, write_json


logger = logging.getLogger(__name__)


RELEVANCE_TERMS = [
    "agent",
    "ai-agent",
    "llm",
    "rag",
    "mcp",
    "model context protocol",
    "autogen",
    "crewai",
    "crew ai",
    "langchain",
    "workflow",
    "coding",
    "assistant",
    "autonomous",
    "multi-agent",
    "multi agent",
    "agentic",
    "browser agent",
    "computer use",
    "openhands",
    "metagpt",
    "semantic kernel",
]

GENERIC_LIST_TERMS = [
    "awesome",
    "roadmap",
    "public api",
    "public-apis",
    "interview",
    "tutorial",
    "cheatsheet",
    "curriculum",
]

LIST_KEEP_TERMS = ["agent", "mcp", "llm", "rag", "autogen", "crewai", "langchain"]


def collect_data(config: dict[str, Any]) -> pd.DataFrame:
    """Collect repository data from GitHub API first, then fallback to sample data."""
    paths = config["paths"]
    github_cfg = config.get("github", {})
    collection_cfg = config.get("collection", {})
    client = GitHubClient(
        base_url=github_cfg.get("base_url", "https://api.github.com"),
        timeout=github_cfg.get("timeout", 20),
        retries=github_cfg.get("retries", 2),
        per_page=github_cfg.get("per_page", 50),
    )
    keywords = list(dict.fromkeys(collection_cfg.get("keywords", [])))
    search_strategies = _search_strategies(github_cfg)
    max_repos = int(github_cfg.get("max_repos", 500))
    per_keyword = int(github_cfg.get("per_keyword_limit", 50))
    readme_limit = int(github_cfg.get("max_readme_repos", 300))
    seed_repos = list(dict.fromkeys(collection_cfg.get("seed_repositories", [])))
    started_at = datetime.now(timezone.utc).isoformat()
    log: dict[str, Any] = {
        "started_at": started_at,
        "mode": "api_live",
        "requested_keywords": keywords,
        "search_strategies": search_strategies,
        "per_keyword_limit": per_keyword,
        "max_repos": max_repos,
        "max_readme_repos": readme_limit,
        "seed_repos_requested": seed_repos,
        "keywords": [],
        "strategy_warnings": [],
    }

    seed_rows, seed_success, seed_failed = _fetch_seed_repositories(client, seed_repos)
    all_rows: list[pd.DataFrame] = []
    if seed_rows:
        all_rows.append(pd.DataFrame(seed_rows))

    raw_items_before_dedup = len(seed_rows)
    for keyword in keywords:
        keyword_log = {"keyword": keyword, "strategies": []}
        for strategy in search_strategies:
            query = f"{keyword} in:name,description,readme archived:false"
            before_failures = client.failure_count
            df = client.search_repositories(
                query,
                max_items=per_keyword,
                sort=strategy.get("sort", "stars"),
                order=strategy.get("order", "desc"),
            )
            rows = int(len(df))
            raw_items_before_dedup += rows
            keyword_log["strategies"].append({"sort": strategy.get("sort"), "order": strategy.get("order"), "rows": rows})
            if client.failure_count > before_failures and rows == 0:
                warning = f"strategy skipped or returned no rows: keyword={keyword}, sort={strategy.get('sort')}"
                log["strategy_warnings"].append(warning)
            if not df.empty:
                all_rows.append(df)
            if _current_dedup_count(all_rows) >= max_repos * 2:
                break
        log["keywords"].append(keyword_log)
        if _current_dedup_count(all_rows) >= max_repos * 2:
            break
        if not all_rows and client.failure_count >= 3:
            logger.warning("GitHub API appears unavailable after repeated failures; switching to fallback if enabled.")
            break

    log["raw_items_before_dedup"] = raw_items_before_dedup
    log["seed_repos_success"] = seed_success
    log["seed_repos_failed"] = seed_failed
    log["github_warnings"] = client.warnings[-20:]
    log["rate_limit"] = client.last_rate_limit

    if all_rows:
        repos = pd.concat(all_rows, ignore_index=True)
        repos = repos.drop_duplicates("full_name").reset_index(drop=True)
        repos["collected_at"] = datetime.now(timezone.utc).isoformat()
        repos["source_type"] = "api_live"
        repos["api_status"] = repos.get("api_status", "ok")
        log["repos_after_dedup"] = int(len(repos))
        repos = _attach_readmes(repos, client, readme_limit, paths)
        repos, filter_meta = apply_relevance_filter(repos, target_min=min(300, max_repos), max_repos=max_repos)
        log.update(filter_meta)
        log["mode"] = "api_live"
        log["repo_count"] = int(len(repos))
        log["fallback_used"] = False
        log["fallback_reason"] = ""
    elif collection_cfg.get("offline_fallback", True):
        logger.warning("GitHub API returned no rows; using sample fallback data.")
        repos = load_sample_fallback(paths["sample_repos"])
        log.update(
            {
                "mode": "sample_fallback",
                "repo_count": int(len(repos)),
                "repos_after_dedup": 0,
                "repos_after_relevance_filter": 0,
                "final_api_live_count": 0,
                "fallback_used": True,
                "fallback_reason": "github_api_no_rows_or_unavailable",
            }
        )
    else:
        raise RuntimeError("GitHub API returned no data and OFFLINE_FALLBACK is false.")

    log["source_type_counts"] = repos["source_type"].value_counts().to_dict()
    if log.get("mode") == "api_live":
        log["final_api_live_count"] = int((repos["source_type"] == "api_live").sum())
    raw_path = project_path(paths["raw_repos"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    repos.to_csv(raw_path, index=False, encoding="utf-8-sig")
    write_json(paths["collection_log"], log | {"finished_at": datetime.now(timezone.utc).isoformat()})
    return repos


def load_sample_fallback(sample_path: str) -> pd.DataFrame:
    """Load deterministic local fallback data and mark it as fallback."""
    path = ensure_sample_data(project_path(sample_path))
    df = pd.read_csv(path)
    df["source_type"] = "sample_fallback"
    df["api_status"] = "sample_fallback"
    return df


def apply_relevance_filter(repos: pd.DataFrame, target_min: int = 300, max_repos: int = 500) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Score and filter repositories using lightweight Agent/LLM relevance signals."""
    data = repos.copy()
    data["agent_relevance_score"] = data.apply(_agent_relevance_score, axis=1)
    strict_threshold = 18.0
    threshold = strict_threshold
    filtered = data[data["agent_relevance_score"] >= threshold].copy()
    relaxed = False
    if len(filtered) < target_min and len(data) >= target_min:
        threshold = 10.0
        filtered = data[data["agent_relevance_score"] >= threshold].copy()
        relaxed = True
    filtered = filtered.sort_values(["agent_relevance_score", "stars_total", "updated_at"], ascending=[False, False, False]).head(max_repos).reset_index(drop=True)
    return filtered, {
        "relevance_threshold": threshold,
        "relevance_filter_relaxed": relaxed,
        "repos_after_relevance_filter": int(len(filtered)),
        "final_api_live_count": int((filtered["source_type"] == "api_live").sum()) if "source_type" in filtered else int(len(filtered)),
        "relevance_score_summary": {
            "min": float(filtered["agent_relevance_score"].min()) if len(filtered) else 0.0,
            "median": float(filtered["agent_relevance_score"].median()) if len(filtered) else 0.0,
            "max": float(filtered["agent_relevance_score"].max()) if len(filtered) else 0.0,
        },
    }


def _fetch_seed_repositories(client: GitHubClient, seed_repos: list[str]) -> tuple[list[dict[str, Any]], list[str], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    success: list[str] = []
    failed: list[dict[str, str]] = []
    for full_name in seed_repos:
        repo = client.get_repository(full_name)
        if repo:
            repo["seed_repository"] = True
            rows.append(repo)
            success.append(full_name)
        else:
            failed.append({"full_name": full_name, "reason": "not_found_or_request_failed"})
    return rows, success, failed


def _search_strategies(github_cfg: dict[str, Any]) -> list[dict[str, str]]:
    configured = github_cfg.get("search_strategies") or [
        {"sort": "stars", "order": "desc"},
        {"sort": "updated", "order": "desc"},
        {"sort": "forks", "order": "desc"},
        {"sort": "best_match", "order": "desc"},
    ]
    return [{"sort": str(item.get("sort", "stars")), "order": str(item.get("order", "desc"))} for item in configured]


def _current_dedup_count(frames: list[pd.DataFrame]) -> int:
    if not frames:
        return 0
    return int(pd.concat(frames, ignore_index=True)["full_name"].nunique())


def _attach_readmes(repos: pd.DataFrame, client: GitHubClient, limit: int, paths: dict[str, str]) -> pd.DataFrame:
    readme_rows = []
    for full_name in repos["full_name"].head(limit):
        readme_rows.append(client.get_readme(str(full_name)))
    readmes = pd.DataFrame(readme_rows)
    readme_path = project_path(paths["raw_readmes"])
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    if not readmes.empty:
        readmes.to_csv(readme_path, index=False, encoding="utf-8-sig")
        merged = repos.merge(readmes[["full_name", "readme_text", "readme_fetch_status"]], on="full_name", how="left")
    else:
        merged = repos.copy()
        merged["readme_text"] = ""
        merged["readme_fetch_status"] = "not_requested"
    merged["readme_text"] = merged["readme_text"].fillna("")
    merged["readme_fetch_status"] = merged["readme_fetch_status"].fillna("not_requested")
    return merged


def _agent_relevance_score(row: pd.Series) -> float:
    name = str(row.get("full_name", "")).lower()
    repo_name = str(row.get("repo_name", "")).lower()
    description = str(row.get("description", "")).lower()
    topics = str(row.get("topics", "")).lower().replace("|", " ")
    readme = str(row.get("readme_text", "")).lower()
    high_signal_text = f"{name} {repo_name} {description} {topics}"
    readme_text = readme[:5000]
    score = 0.0
    for term in RELEVANCE_TERMS:
        if term in high_signal_text:
            score += 10.0
        elif term in readme_text:
            score += 3.0
    if re.search(r"\bagent(s)?\b", high_signal_text):
        score += 12.0
    if re.search(r"\b(llm|rag|mcp)\b", high_signal_text):
        score += 10.0
    if bool(row.get("seed_repository", False)):
        score += 35.0
    generic_hits = [term for term in GENERIC_LIST_TERMS if term in high_signal_text]
    keep_hits = [term for term in LIST_KEEP_TERMS if term in high_signal_text]
    if generic_hits and not keep_hits:
        score -= 18.0
    elif generic_hits and keep_hits:
        score -= 4.0
    if "awesome" in repo_name and ("agent" in repo_name or "mcp" in repo_name or "llm" in repo_name):
        score += 8.0
    return float(max(0.0, min(score, 100.0)))
