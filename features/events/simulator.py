from __future__ import annotations

from .models import Event, EventResponse, EventResult, SimulationResult


def apply_event(
    simulation_result: SimulationResult,
    event: Event,
    response: EventResponse | None = None,
) -> EventResult:
    """Apply an event and an optional response without mutating the input."""
    if response is not None and response not in event.responses:
        raise ValueError(f"Response {response.name!r} is not available for {event.name!r}")

    deltas = dict(event.metric_deltas)
    budget_delta = 0.0
    if response is not None:
        for metric, delta in response.metric_deltas.items():
            deltas[metric] = deltas.get(metric, 0.0) + delta
        budget_delta = response.budget_cost

    return EventResult(
        result=simulation_result.with_changes(deltas, budget_delta),
        event=event,
        response=response,
        applied_deltas=deltas,
    )
