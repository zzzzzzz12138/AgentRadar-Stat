from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ROLE_OPTIONS = [
    "快速了解 AI Agent 生态的学习者",
    "想选择学习/复现项目的开发者",
    "寻找课程项目/创新实践方向的学习者",
    "技术社区观察者",
    "开源项目维护者",
    "AI 工具与软件工程研究者",
    "其他",
]

GOAL_OPTIONS = [
    "快速了解趋势",
    "选择可复现项目",
    "寻找课程项目",
    "寻找科研入门方向",
    "寻找开源贡献对象",
    "评估技术生态",
    "生成 Codex 开发 Prompt",
    "比较项目风险",
]

LEVEL_OPTIONS = ["入门", "中等", "熟练", "高阶"]
LANGUAGE_OPTIONS = ["Python", "TypeScript", "JavaScript", "Go", "Rust", "Java", "C++", "无明显偏好"]
TOPIC_OPTIONS = [
    "Coding Agent",
    "RAG Agent",
    "MCP Tool",
    "Workflow Agent",
    "Research Agent",
    "Data Agent",
    "Multimodal Agent",
    "AutoML Agent",
    "Local LLM",
    "Agent Framework",
]
HARDWARE_OPTIONS = ["本地普通电脑", "有独立显卡", "云端资源可用", "不确定"]
RISK_OPTIONS = ["低风险稳健", "平衡", "愿意尝试前沿高风险项目"]
OUTPUT_OPTIONS = ["想要排行榜", "想要三天复现路线", "想要学习路径", "想要技术对比", "想要 Codex Prompt", "想要研究选题建议"]

DEFAULT_USER_ROLE = "想选择学习/复现项目的开发者"
DEFAULT_MAIN_GOAL = "选择可复现项目"
DEFAULT_PROGRAMMING_LEVEL = "中等"
DEFAULT_HARDWARE_CONDITION = "本地普通电脑"
DEFAULT_RISK_PREFERENCE = "平衡"


@dataclass(slots=True)
class UserProfile:
    """Local, non-identifying preference profile for project recommendation."""

    user_role: str = DEFAULT_USER_ROLE
    main_goal: str = DEFAULT_MAIN_GOAL
    programming_level: str = DEFAULT_PROGRAMMING_LEVEL
    preferred_languages: list[str] = field(default_factory=lambda: ["Python"])
    preferred_topics: list[str] = field(default_factory=lambda: ["Coding Agent", "RAG Agent"])
    hardware_condition: str = DEFAULT_HARDWARE_CONDITION
    risk_preference: str = DEFAULT_RISK_PREFERENCE
    output_preference: list[str] = field(default_factory=lambda: ["想要排行榜", "想要三天复现路线", "想要 Codex Prompt"])

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable profile without credentials or private identifiers."""
        return asdict(self)


def default_user_profile() -> UserProfile:
    """Return the classroom/demo default profile used by batch pipeline outputs."""
    return UserProfile()


def build_user_profile_from_dict(data: dict[str, Any] | None) -> UserProfile:
    """Normalize UI/session data into a validated UserProfile."""
    data = data or {}
    return UserProfile(
        user_role=_pick(data.get("user_role"), ROLE_OPTIONS, DEFAULT_USER_ROLE),
        main_goal=_pick(data.get("main_goal"), GOAL_OPTIONS, DEFAULT_MAIN_GOAL),
        programming_level=_pick(data.get("programming_level"), LEVEL_OPTIONS, DEFAULT_PROGRAMMING_LEVEL),
        preferred_languages=_multi(data.get("preferred_languages"), LANGUAGE_OPTIONS, ["Python"]),
        preferred_topics=_multi(data.get("preferred_topics"), TOPIC_OPTIONS, ["Coding Agent", "RAG Agent"]),
        hardware_condition=_pick(data.get("hardware_condition"), HARDWARE_OPTIONS, DEFAULT_HARDWARE_CONDITION),
        risk_preference=_pick(data.get("risk_preference"), RISK_OPTIONS, DEFAULT_RISK_PREFERENCE),
        output_preference=_multi(data.get("output_preference"), OUTPUT_OPTIONS, ["想要排行榜", "想要三天复现路线"]),
    )


def _pick(value: Any, options: list[str], default: str) -> str:
    if value == "CPU-only":
        return "本地普通电脑"
    if value in {"有普通 GPU", "有较强 GPU"}:
        return "有独立显卡"
    return value if isinstance(value, str) and value in options else default


def _multi(value: Any, options: list[str], default: list[str]) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return list(default)
    picked = [item for item in value if isinstance(item, str) and item in options]
    return picked or list(default)
