from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .utils import project_path


logger = logging.getLogger(__name__)


class DeepSeekClient:
    """OpenAI-compatible DeepSeek client with safe fallback responses."""

    def __init__(
        self,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-v4-pro",
        log_path: str | Path = "outputs/agents/agent_call_log.jsonl",
    ) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", base_url)
        self.model = os.getenv("DEEPSEEK_MODEL", model)
        self.log_path = project_path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 900,
        timeout: int = 45,
        expect_json: bool = False,
        fallback_message: str = "DeepSeek API unavailable; fallback response generated.",
    ) -> dict[str, Any]:
        """Call DeepSeek chat completions and return content plus status metadata."""
        if not self.api_key:
            result = self._fallback("missing_api_key", fallback_message)
            self._log_call(messages, result)
            return result
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=timeout)
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = completion.choices[0].message.content or ""
            parsed_json = None
            if expect_json:
                parsed_json = self.parse_json(content)
            result = {
                "content": content,
                "json": parsed_json,
                "api_call_status": "ok",
                "fallback_used": False,
                "model": self.model,
            }
            self._log_call(messages, result)
            return result
        except Exception as exc:  # noqa: BLE001 - external API failures must not crash pipeline.
            logger.warning("DeepSeek API call failed: %s", exc)
            result = self._fallback(type(exc).__name__, fallback_message)
            self._log_call(messages, result)
            return result

    @staticmethod
    def parse_json(content: str) -> Any | None:
        """Parse a JSON response, tolerating fenced Markdown blocks."""
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json\n", "", 1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _fallback(self, reason: str, message: str) -> dict[str, Any]:
        return {
            "content": message,
            "json": None,
            "api_call_status": reason,
            "fallback_used": True,
            "model": self.model,
        }

    def _log_call(self, messages: list[dict[str, str]], result: dict[str, Any]) -> None:
        safe_record = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model": self.model,
            "base_url": self.base_url,
            "message_count": len(messages),
            "api_call_status": result.get("api_call_status"),
            "fallback_used": result.get("fallback_used"),
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(safe_record, ensure_ascii=False) + "\n")
