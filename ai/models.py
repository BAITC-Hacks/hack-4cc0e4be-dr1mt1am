"""Explanation-only output schema and controlled integration errors."""

import json
from dataclasses import dataclass
from typing import Any


class AIAnalysisError(Exception):
    """Base error for UI integration. Messages never include provider response bodies."""

    code = "AI_ANALYSIS_ERROR"


class InvalidSimulationError(AIAnalysisError, ValueError):
    code = "SIMULATION_INVALID"


class MissingAPIKeyError(AIAnalysisError):
    code = "API_KEY_MISSING"


class AIRequestError(AIAnalysisError):
    code = "OPENAI_REQUEST_FAILED"

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AIResponseError(AIAnalysisError):
    code = "AI_RESPONSE_INVALID"


@dataclass(frozen=True)
class AIAnalysis:
    summary: str
    strengths: list[str]
    risks: list[str]
    tradeoffs: list[str]
    recommendations: list[str]

    @classmethod
    def from_json(cls, text: str) -> "AIAnalysis":
        """Validate a completed Structured Output without coercing or inventing fields."""
        try:
            value = json.loads(text)
        except (ValueError, TypeError):
            raise AIResponseError("OpenAI вернул некорректный JSON анализа.") from None
        if not isinstance(value, dict) or set(value) != set(ANALYSIS_SCHEMA["required"]):
            raise AIResponseError("Структура ответа OpenAI не соответствует AIAnalysis.")
        if not isinstance(value["summary"], str):
            raise AIResponseError("Поле summary должно быть строкой.")
        for name in ("strengths", "risks", "tradeoffs", "recommendations"):
            if not isinstance(value[name], list) or not all(isinstance(item, str) for item in value[name]):
                raise AIResponseError(f"Поле {name} должно быть списком строк.")
        return cls(**value)


ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "tradeoffs": {"type": "array", "items": {"type": "string"}},
        "recommendations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "strengths", "risks", "tradeoffs", "recommendations"],
    "additionalProperties": False,
}
