from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


THEMES = [
    ("coding-agent", "Coding Agent", "Python", ["coding-agent", "codex", "automation"]),
    ("rag-agent", "RAG Agent", "Python", ["rag", "llm", "retrieval"]),
    ("research-agent", "Research Agent", "TypeScript", ["research-agent", "paper", "workflow"]),
    ("workflow-agent", "Workflow Agent", "Python", ["workflow-agent", "orchestration", "agentic-ai"]),
    ("mcp-tool", "MCP Tool", "TypeScript", ["mcp", "tooling", "developer-tools"]),
    ("multimodal-agent", "Multimodal Agent", "Python", ["multimodal", "vision-language", "agent"]),
    ("automl-agent", "AutoML Agent", "Python", ["automl", "mlops", "agent"]),
    ("data-agent", "Data Agent", "Jupyter Notebook", ["data-agent", "analytics", "pandas"]),
]


def ensure_sample_data(path: str | Path, rows: int = 180) -> Path:
    """Create deterministic fallback sample data if it does not exist."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and len(pd.read_csv(target)) >= 150:
        return target

    rng = np.random.default_rng(42)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    records = []
    for i in range(rows):
        slug, theme, language, topics = THEMES[i % len(THEMES)]
        cohort = i % 5
        age_days = int(rng.integers(20, 2200))
        if cohort == 0:  # short-term surge
            age_days = int(rng.integers(20, 180))
            stars = int(rng.lognormal(7.1, 0.55))
            weekly = int(stars * rng.uniform(0.10, 0.35))
            update_gap = int(rng.integers(0, 12))
        elif cohort == 1:  # high star, low maintenance
            stars = int(rng.lognormal(8.2, 0.45))
            weekly = int(stars * rng.uniform(0.001, 0.01))
            update_gap = int(rng.integers(280, 900))
        elif cohort == 2:  # reproducible docs
            stars = int(rng.lognormal(6.7, 0.5))
            weekly = int(stars * rng.uniform(0.01, 0.06))
            update_gap = int(rng.integers(0, 45))
        elif cohort == 3:  # high risk
            stars = int(rng.lognormal(6.5, 0.7))
            weekly = int(stars * rng.uniform(0.0, 0.03))
            update_gap = int(rng.integers(120, 600))
        else:  # low star, high potential
            age_days = int(rng.integers(10, 120))
            stars = int(rng.integers(40, 700))
            weekly = int(stars * rng.uniform(0.08, 0.30))
            update_gap = int(rng.integers(0, 10))

        forks = max(1, int(stars * rng.uniform(0.04, 0.22)))
        issues = max(0, int((forks * rng.uniform(0.05, 0.7)) + (35 if cohort == 3 else 0)))
        readme_blocks = [
            f"# {theme} Lab {i:03d}",
            "This project explores AI agent workflows for learning, automation, and reproducible experiments.",
            "## Installation\npip install -r requirements.txt",
        ]
        if cohort in {0, 2, 4}:
            readme_blocks.extend(["## Quickstart\nRun python main.py to launch the demo.", "## Demo\nIncludes examples and screenshots."])
        if cohort in {2, 4}:
            readme_blocks.extend(["## CPU Friendly\nRuns on CPU-only Windows 11 environments.", "## Docker\nA Dockerfile example is provided."])
        if cohort == 3:
            readme_blocks.extend(["Requires GPU acceleration and multiple API key providers.", "Experimental status; issues may be stale."])
        readme_text = "\n\n".join(readme_blocks + [f"Topics: {', '.join(topics)}"] * int(rng.integers(1, 6)))
        created = now - timedelta(days=age_days)
        updated = now - timedelta(days=update_gap)
        pushed = updated - timedelta(days=int(rng.integers(0, 5)))
        owner = f"agent-lab-{i % 17:02d}"
        repo = f"{slug}-radar-{i:03d}"
        records.append(
            {
                "repo_id": 900000 + i,
                "owner": owner,
                "repo_name": repo,
                "full_name": f"{owner}/{repo}",
                "repo_url": f"https://github.com/{owner}/{repo}",
                "description": f"{theme} toolkit for AI Agent ecosystem analysis and course demos.",
                "language": language,
                "topics": "|".join(topics),
                "stars_total": stars,
                "forks_total": forks,
                "watchers_total": max(1, int(stars * rng.uniform(0.2, 0.9))),
                "open_issues_count": issues,
                "created_at": created.isoformat(),
                "updated_at": updated.isoformat(),
                "pushed_at": pushed.isoformat(),
                "license": rng.choice(["MIT", "Apache-2.0", "BSD-3-Clause", "NOASSERTION"]),
                "default_branch": "main",
                "has_issues": True,
                "has_wiki": bool(rng.integers(0, 2)),
                "has_pages": bool(rng.integers(0, 2)),
                "archived": cohort == 1 and bool(rng.integers(0, 3) == 0),
                "size": int(rng.integers(800, 90000)),
                "stars_this_week": weekly,
                "readme_text": readme_text,
                "collected_at": now.isoformat(),
                "source_type": "sample_fallback",
                "api_status": "sample_fallback",
            }
        )
    pd.DataFrame(records).to_csv(target, index=False, encoding="utf-8-sig")
    return target
