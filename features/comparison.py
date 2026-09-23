from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .events.models import SimulationResult


@dataclass(frozen=True)
class ScenarioSummary:
    name: str
    score: float
    budget_used: float
    critical_count: int
    critical_metrics: tuple[str, ...]
    weakest_metric: str | None
    metrics: Mapping[str, float]


def summarize_scenario(
    name: str,
    result: SimulationResult,
    score: float,
    critical_threshold: float = 0.0,
) -> ScenarioSummary:
    critical_metrics = tuple(
        metric for metric, value in result.metrics.items() if value < critical_threshold
    )
    weakest_metric = min(result.metrics, key=result.metrics.get, default=None)
    return ScenarioSummary(
        name=name,
        score=score,
        budget_used=result.budget_used,
        critical_count=len(critical_metrics),
        critical_metrics=critical_metrics,
        weakest_metric=weakest_metric,
        metrics=dict(result.metrics),
    )


def compare_scenarios(scenarios: Iterable[ScenarioSummary]) -> list[dict[str, object]]:
    """Return stable row data suitable for a CLI, API, or UI table."""
    rows = []
    for scenario in scenarios:
        rows.append(
            {
                "name": scenario.name,
                "budget": scenario.budget_used,
                "score": scenario.score,
                "critical": scenario.critical_count,
                "critical_metrics": scenario.critical_metrics,
                "weakest": scenario.weakest_metric,
            }
        )
    return rows
