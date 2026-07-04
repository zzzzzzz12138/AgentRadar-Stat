from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Allow the scaffold to run before dependencies are installed.
    def load_dotenv(*_: Any, **__: Any) -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def setup_logging() -> None:
    """Configure console and file logging for the whole project."""
    log_dir = PROJECT_ROOT / "outputs" / "reports"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "agent_radar.log", encoding="utf-8"),
        ],
        force=True,
    )
    for noisy_logger in ["httpx", "httpcore", "openai"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def load_config(config_path: str | Path = "config.yaml") -> dict[str, Any]:
    """Load .env and config.yaml, then apply environment overrides."""
    load_dotenv(PROJECT_ROOT / ".env")
    path = PROJECT_ROOT / config_path
    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    github = config.setdefault("github", {})
    deepseek = config.setdefault("deepseek", {})
    collection = config.setdefault("collection", {})

    github["max_repos"] = int(os.getenv("MAX_REPOS", github.get("max_repos", 300)))
    github["per_keyword_limit"] = int(os.getenv("PER_KEYWORD_LIMIT", github.get("per_keyword_limit", 50)))
    github["max_readme_repos"] = int(os.getenv("MAX_README_REPOS", github.get("max_readme_repos", 120)))
    deepseek["base_url"] = os.getenv("DEEPSEEK_BASE_URL", deepseek.get("base_url", "https://api.deepseek.com"))
    deepseek["model"] = os.getenv("DEEPSEEK_MODEL", deepseek.get("model", "deepseek-v4-pro"))
    deepseek["use_agents"] = str(os.getenv("USE_DEEPSEEK_AGENTS", deepseek.get("use_agents", True))).lower() == "true"
    collection["offline_fallback"] = str(os.getenv("OFFLINE_FALLBACK", collection.get("offline_fallback", True))).lower() == "true"
    collection["max_agent_repos"] = int(os.getenv("MAX_AGENT_REPOS", collection.get("max_agent_repos", 30)))
    return config


def ensure_directories(config: dict[str, Any]) -> None:
    """Create standard project directories if they do not already exist."""
    for directory in [
        "data/raw",
        "data/processed",
        "data/sample",
        "outputs/figures",
        "outputs/reports",
        "outputs/dashboards",
        "outputs/models",
        "outputs/agents",
        "docs",
        "notebooks",
        "tests",
    ]:
        (PROJECT_ROOT / directory).mkdir(parents=True, exist_ok=True)
    for key, value in config.get("paths", {}).items():
        if key.endswith("_dir"):
            (PROJECT_ROOT / value).mkdir(parents=True, exist_ok=True)


def project_path(path: str | Path) -> Path:
    """Resolve a path relative to the repository root."""
    return PROJECT_ROOT / path


def write_json(path: str | Path, data: Any) -> None:
    """Write JSON with UTF-8 and stable indentation."""
    target = project_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
