"""OpenAI Responses API adapter with strict explanation-only Structured Outputs."""

import json
import os
from copy import deepcopy

from openai import APIError, APIResponseValidationError, OpenAI

from engine.models import SimulationResult

from .models import (
    AIAnalysis, AIRequestError, AIResponseError, ANALYSIS_SCHEMA,
    InvalidSimulationError, MissingAPIKeyError,
)
from .payload import build_analysis_payload
from .prompts import ANALYSIS_INSTRUCTIONS


def get_model_name() -> str:
    return os.environ.get("OPENAI_MODEL", "").strip() or "gpt-5.6-terra"


def analyze_simulation(result: SimulationResult, client: OpenAI | None = None) -> AIAnalysis:
    """Explain a valid result. Injected clients own their credentials and lifecycle."""
    payload = build_analysis_payload(result)
    try:
        serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True)
    except (ValueError, TypeError):
        raise InvalidSimulationError("Результат симуляции содержит некорректные данные.") from None

    if client is not None:
        return _request_analysis(client, serialized)

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise MissingAPIKeyError("Задайте OPENAI_API_KEY в окружении для AI-анализа.")
    with OpenAI(api_key=api_key, timeout=30.0, max_retries=0) as owned_client:
        return _request_analysis(owned_client, serialized)


def _request_analysis(client: OpenAI, payload: str) -> AIAnalysis:
    try:
        response = client.responses.create(
            model=get_model_name(),
            instructions=ANALYSIS_INSTRUCTIONS,
            input=[{"role": "user", "content": payload}],
            text={"format": {
                "type": "json_schema", "name": "city_simulation_analysis",
                "strict": True, "schema": deepcopy(ANALYSIS_SCHEMA),
            }},
            store=False,
        )
    except APIResponseValidationError:
        raise AIResponseError("OpenAI вернул неожиданный формат ответа API.") from None
    except APIError as error:
        # Do not expose provider bodies, request headers, credentials, or raw causes.
        raise AIRequestError(
            "Не удалось выполнить запрос к OpenAI.",
            status_code=getattr(error, "status_code", None),
        ) from None

    if getattr(response, "status", None) == "failed":
        raise AIRequestError("OpenAI сообщил об ошибке выполнения запроса.")
    if getattr(response, "status", None) != "completed":
        raise AIResponseError("OpenAI не вернул завершённый анализ.")
    output = getattr(response, "output", None)
    if not isinstance(output, (list, tuple)):
        raise AIResponseError("OpenAI вернул некорректную структуру результата.")
    for item in output:
        contents = getattr(item, "content", ())
        if not isinstance(contents, (list, tuple)):
            raise AIResponseError("OpenAI вернул некорректную структуру сообщения.")
        for content in contents:
            if getattr(content, "type", None) == "refusal":
                raise AIResponseError("Модель отказалась формировать анализ.")
    try:
        text = getattr(response, "output_text", None)
    except (AttributeError, TypeError):
        raise AIResponseError("OpenAI вернул некорректную структуру текста.") from None
    if not isinstance(text, str) or not text.strip():
        raise AIResponseError("OpenAI вернул пустой или неожиданный ответ.")
    return AIAnalysis.from_json(text)
