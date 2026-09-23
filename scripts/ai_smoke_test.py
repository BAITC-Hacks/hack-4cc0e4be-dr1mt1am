"""Manual OpenAI smoke test. Run from the repository's Python environment."""

import os
from pathlib import Path
import sys

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
    except AIRequestError:
        print(
            "Ошибка запроса к OpenAI. Проверьте подключение, ключ и доступ к модели.",
            file=sys.stderr,
        )
        return 3
    except AIResponseError:
        print("Некорректный ответ AI: анализ не получен в ожидаемом формате.", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    # Keep Russian output readable when Windows redirects stdout/stderr to pipes.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
