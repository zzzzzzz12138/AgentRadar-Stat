from __future__ import annotations

import base64
import logging
import os
import time
from typing import Any

import pandas as pd
import requests


logger = logging.getLogger(__name__)


class GitHubClient:
    """Small GitHub REST API client with retries, timeout, and safe failures."""

    def __init__(
        self,
        base_url: str = "https://api.github.com",
        timeout: int = 20,
        retries: int = 2,
        per_page: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.per_page = min(int(per_page), 100)
        self.session = requests.Session()
        self.failure_count = 0
        self.warnings: list[str] = []
        self.last_rate_limit: dict[str, Any] = {}
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AgentRadar-Stat/0.1",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            self.headers["Authorization"] = "Bearer " + token

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> Any | None:
        """Request an endpoint and return decoded JSON, or None after logged errors."""
        url = endpoint if endpoint.startswith("http") else self.base_url + endpoint
        for attempt in range(self.retries + 1):
            try:
                resp = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
                remaining = resp.headers.get("X-RateLimit-Remaining")
                self.last_rate_limit = {
                    "remaining": remaining,
                    "limit": resp.headers.get("X-RateLimit-Limit"),
                    "reset": resp.headers.get("X-RateLimit-Reset"),
                }
                if resp.status_code == 403 and remaining == "0":
                    reset = int(resp.headers.get("X-RateLimit-Reset", "0") or 0)
                    sleep_for = max(0, min(reset - int(time.time()), 60))
                    logger.warning("GitHub API rate limit reached; sleeping %s seconds", sleep_for)
                    time.sleep(sleep_for)
                    continue
                if resp.status_code >= 400:
                    self.failure_count += 1
                    warning = f"GitHub API error {resp.status_code} at {endpoint}: {resp.text[:180]}"
                    self.warnings.append(warning)
                    logger.warning("%s", warning)
                    if attempt < self.retries and resp.status_code in {429, 500, 502, 503, 504}:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    return None
                return resp.json()
            except requests.RequestException as exc:
                self.failure_count += 1
                warning = f"GitHub request failed at {endpoint}: {exc}"
                self.warnings.append(warning)
                logger.warning("%s", warning)
                if attempt < self.retries:
                    time.sleep(1.5 * (attempt + 1))
        return None

    def search_repositories(self, query: str, max_items: int = 30, sort: str = "stars", order: str = "desc") -> pd.DataFrame:
        """Search public repositories and return normalized repository rows."""
        rows: list[dict[str, Any]] = []
        pages = max(1, (max_items + self.per_page - 1) // self.per_page)
        for page in range(1, pages + 1):
            params: dict[str, Any] = {
                "q": query,
                "order": order,
                "per_page": min(self.per_page, max_items - len(rows)),
                "page": page,
            }
            if sort and sort != "best_match":
                params["sort"] = sort
            payload = self._request(
                "/search/repositories",
                params,
            )
            if not payload or "items" not in payload:
                break
            rows.extend(self._normalize_repo(item) for item in payload.get("items", []))
            if len(rows) >= max_items:
                break
        return pd.DataFrame(rows)

    def get_repository(self, full_name: str) -> dict[str, Any] | None:
        """Fetch a single repository detail by owner/repo."""
        payload = self._request(f"/repos/{full_name}")
        return self._normalize_repo(payload) if payload else None

    def get_readme(self, full_name: str) -> dict[str, Any]:
        """Fetch and decode README content; never raises for a single repo failure."""
        payload = self._request(f"/repos/{full_name}/readme")
        if not payload or "content" not in payload:
            return {"full_name": full_name, "readme_text": "", "readme_fetch_status": "failed"}
        try:
            text = base64.b64decode(payload["content"]).decode("utf-8", errors="ignore")
            return {"full_name": full_name, "readme_text": text, "readme_fetch_status": "ok"}
        except Exception as exc:  # noqa: BLE001 - decoding failures are non-fatal.
            logger.warning("README decode failed for %s: %s", full_name, exc)
            return {"full_name": full_name, "readme_text": "", "readme_fetch_status": "decode_failed"}

    def get_recent_prs(self, full_name: str, max_items: int = 10) -> list[dict[str, Any]]:
        """Optionally fetch recent pull requests for a repository."""
        payload = self._request(f"/repos/{full_name}/pulls", {"state": "all", "per_page": max_items, "sort": "updated"})
        return payload if isinstance(payload, list) else []

    @staticmethod
    def _normalize_repo(repo: dict[str, Any]) -> dict[str, Any]:
        owner = (repo.get("owner") or {}).get("login", "")
        return {
            "repo_id": repo.get("id"),
            "owner": owner,
            "repo_name": repo.get("name", ""),
            "full_name": repo.get("full_name", ""),
            "repo_url": repo.get("html_url", ""),
            "description": repo.get("description") or "",
            "language": repo.get("language") or "Unknown",
            "topics": "|".join(repo.get("topics") or []),
            "stars_total": repo.get("stargazers_count", 0),
            "forks_total": repo.get("forks_count", 0),
            "watchers_total": repo.get("watchers_count", 0),
            "open_issues_count": repo.get("open_issues_count", 0),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "license": (repo.get("license") or {}).get("spdx_id", "NOASSERTION"),
            "default_branch": repo.get("default_branch", "main"),
            "has_issues": repo.get("has_issues", False),
            "has_wiki": repo.get("has_wiki", False),
            "has_pages": repo.get("has_pages", False),
            "archived": repo.get("archived", False),
            "size": repo.get("size", 0),
            "stars_this_week": 0,
            "api_status": "ok",
        }
