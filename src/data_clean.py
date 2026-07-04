from __future__ import annotations

import re
from typing import Any

import pandas as pd

from .data_collect import load_sample_fallback
from .utils import project_path


NUMERIC_COLUMNS = ["stars_total", "forks_total", "watchers_total", "open_issues_count", "size", "stars_this_week"]
DATE_COLUMNS = ["created_at", "updated_at", "pushed_at", "collected_at"]


def clean_data(config: dict[str, Any]) -> pd.DataFrame:
    """读取原始采集数据并输出清洗后的仓库表。"""
    paths = config["paths"]
    raw_path = project_path(paths["raw_repos"])
    if raw_path.exists():
        df = pd.read_csv(raw_path)
    else:
        # 原始 API 文件不存在时，说明采集阶段失败或尚未运行，使用兜底样本。
        df = load_sample_fallback(paths["sample_repos"])
    df = normalize_schema(df)
    df = deduplicate_repos(df)
    df = fill_missing_values(df)
    df = convert_types(df)
    df["readme_text"] = df["readme_text"].map(clean_readme_text)
    df["api_status"] = df["api_status"].fillna("unknown")
    out_path = project_path(paths["cleaned_repos"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return df


def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """补齐第一阶段需要的标准字段，避免后续模块因为缺列中断。"""
    required_defaults = {
        "repo_id": 0,
        "owner": "",
        "repo_name": "",
        "full_name": "",
        "repo_url": "",
        "description": "",
        "language": "Unknown",
        "topics": "",
        "license": "NOASSERTION",
        "default_branch": "main",
        "has_issues": True,
        "has_wiki": False,
        "has_pages": False,
        "archived": False,
        "readme_text": "",
        "source_type": "api_live",
        "api_status": "unknown",
    }
    for column in NUMERIC_COLUMNS:
        required_defaults[column] = 0
    now = pd.Timestamp.utcnow().isoformat()
    for column in DATE_COLUMNS:
        required_defaults[column] = now
    for column, default in required_defaults.items():
        if column not in df.columns:
            df[column] = default
    missing_names = df["full_name"].astype(str).str.len() == 0
    df.loc[missing_names, "full_name"] = df.loc[missing_names, "owner"].astype(str) + "/" + df.loc[missing_names, "repo_name"].astype(str)
    return df


def deduplicate_repos(df: pd.DataFrame) -> pd.DataFrame:
    """按照 full_name 去重，保留第一条记录。"""
    # GitHub full_name 是 owner/repo，适合作为公开仓库的唯一标识。
    return df.drop_duplicates("full_name").reset_index(drop=True)


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """填补文本、布尔和数值字段的缺失值。"""
    text_columns = ["description", "language", "topics", "license", "default_branch", "readme_text", "source_type", "api_status"]
    for column in text_columns:
        df[column] = df[column].fillna("" if column != "language" else "Unknown")
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    for column in ["has_issues", "has_wiki", "has_pages", "archived"]:
        df[column] = df[column].fillna(False).astype(bool)
    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """转换数值和时间字段类型，并保留 UTC 时间信息。"""
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)
    now = pd.Timestamp.utcnow()
    for column in DATE_COLUMNS:
        df[column] = df[column].fillna(now)
    return df


def clean_readme_text(text: Any) -> str:
    """清洗 README 文本，移除 Markdown 链接、代码块和多余空白。"""
    if not isinstance(text, str):
        return ""
    # 先去掉代码块，再删除链接标记，保留可用于关键词识别的自然语言。
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#>*_`~\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
