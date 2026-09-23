"""Manual OpenAI smoke test. Run from the repository's Python environment."""

import os
from pathlib import Path
import re
import sys

from openai import APIError

# Support `python scripts/ai_smoke_test.py` without installing the project.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.analyzer import analyze_simulation, get_model_name
from ai.models import (
    AIRequestError,
    AIResponseError,
    InvalidSimulationError,
    MissingAPIKeyError,
)
from engine.models import Decision
from engine.simulator import simulate_scenario


def safe_error_text(value: object) -> str:
    """Render scalar diagnostics only, redacting credentials before truncation."""
    if not isinstance(value, (str, int)):
        return "недоступно"
    text = str(value)
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        text = text.replace(key, "[REDACTED]")
    # API authentication messages may echo another key or a masked key fragment.
    text = re.sub(r"\bsk-[\w.*…-]+", "[REDACTED]", text)
    if re.search(r"headers?|authorization|bearer|client", text, re.IGNORECASE):
        return "[Сообщение скрыто: содержит служебные или конфиденциальные данные]"
    text = "".join(char if char.isprintable() else " " for char in text)
    return text[:2000] or "недоступно"


def print_api_error(error: Exception) -> None:
    """Inspect only allowed fields; never dump exceptions, requests, or clients."""
    source: BaseException = error
    seen: set[int] = set()
    while id(source) not in seen:
        seen.add(id(source))
        if isinstance(source, APIError):
            break
        parent = source.__cause__ or source.__context__
        if parent is None:
            break
        source = parent
    if not isinstance(source, APIError):
        source = error

    body = source.body if isinstance(source, APIError) else None
    details = body if isinstance(body, dict) else {}
    if isinstance(details.get("error"), dict):
        details = details["error"]
    message = details.get("message")
    if not isinstance(message, str):
        # SDK status messages can contain the entire response body. Do not print it.
        if isinstance(source, APIError):
            message = source.message if body is None else "Текст сообщения API недоступен."
        else:
            message = error.args[0] if error.args else None

    fields = (
        ("Exception", type(source).__name__),
        ("HTTP status", getattr(source, "status_code", getattr(error, "status_code", None))),
        ("Error code", details.get("code", getattr(source, "code", None))),
        ("Error type", details.get("type", getattr(source, "type", None))),
        ("Message", message),
    )
    for label, value in fields:
        print(f"{label}: {safe_error_text(value)}", file=sys.stderr)


def run_smoke_test() -> None:
    result = simulate_scenario(
        [
            Decision("M7", "Nura"),
            Decision("M8", "Nura"),
            Decision("M10", "Nura"),
            Decision("M12"),
            Decision("M5", "Saryarka"),
        ]
    )
    if not result.valid:
        raise InvalidSimulationError("Эталонный сценарий не прошёл валидацию.")

    scores = (result.score_before, result.score_after, result.score_delta)
    for label, value in zip(("Baseline Score", "Scenario Score", "Delta"), scores):
        if value is None:
            raise InvalidSimulationError("В результате симуляции отсутствует Score.")
        print(f"{label}: {value:.5f}")
    print(f"Budget used: {result.budget_used}")
    print(f"Budget remaining: {result.budget_remaining}")
    print(f"N_crit before: {result.n_crit_before}")
    print(f"N_crit after: {result.n_crit_after}")
    print("Triggered synergies:")
    for triggered in result.triggered_synergies:
        synergy = triggered.synergy
        print(
            f"* {synergy.first_initiative_id} + {synergy.second_initiative_id}"
            f" -> {triggered.district}"
        )

    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise MissingAPIKeyError("OPENAI_API_KEY не задан.")

    print(f"Model: {get_model_name()}", flush=True)
    analysis = analyze_simulation(result)
    print(f"\nSUMMARY\n{analysis.summary}")
    for heading, items in (
        ("STRENGTHS", analysis.strengths),
        ("RISKS", analysis.risks),
        ("TRADE-OFFS", analysis.tradeoffs),
        ("RECOMMENDATIONS", analysis.recommendations),
    ):
        print(f"\n{heading}")
        for item in items:
            print(f"* {item}")


def main() -> int:
    try:
        run_smoke_test()
    except InvalidSimulationError:
        print("Ошибка симуляции: сценарий невалиден или результат неполон.", file=sys.stderr)
        return 1
    except MissingAPIKeyError:
        print(
            "OPENAI_API_KEY не задан. "
            "Установите переменную окружения и запустите smoke test снова.",
            file=sys.stderr,
        )
        return 2
    except (AIRequestError, APIError) as error:
        print(
            "Ошибка запроса к OpenAI. Проверьте подключение, ключ и доступ к модели.",
            file=sys.stderr,
        )
        print_api_error(error)
        return 3
    except AIResponseError as error:
        print("Некорректный ответ AI: анализ не получен в ожидаемом формате.", file=sys.stderr)
        print_api_error(error)
        return 4
    return 0


if __name__ == "__main__":
    # Keep Russian output readable when Windows redirects stdout/stderr to pipes.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
