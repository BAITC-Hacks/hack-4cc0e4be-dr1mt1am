from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping


@dataclass(frozen=True)
class SimulationResult:
    """A small adapter-friendly snapshot passed between optional features."""

    metrics: Mapping[str, float]
    budget_used: float = 0.0
    decisions: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def with_changes(
        self,
        metric_deltas: Mapping[str, float],
        budget_delta: float = 0.0,
    ) -> "SimulationResult":
        metrics = dict(self.metrics)
        for metric, delta in metric_deltas.items():
            metrics[metric] = metrics.get(metric, 0.0) + delta
        return replace(self, metrics=metrics, budget_used=self.budget_used + budget_delta)


@dataclass(frozen=True)
class EventResponse:
    name: str
    metric_deltas: Mapping[str, float] = field(default_factory=dict)
    budget_cost: float = 0.0


@dataclass(frozen=True)
class Event:
    name: str
    description: str
    metric_deltas: Mapping[str, float] = field(default_factory=dict)
    responses: tuple[EventResponse, ...] = ()


@dataclass(frozen=True)
class EventResult:
    result: SimulationResult
    event: Event
    response: EventResponse | None
    applied_deltas: Mapping[str, float]
