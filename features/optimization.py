from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Sequence

from .comparison import ScenarioSummary, summarize_scenario
from .events.models import SimulationResult


@dataclass(frozen=True)
class CandidateScenario:
    decisions: tuple[object, ...]

    @property
    def selected_initiatives(self) -> tuple[str, ...]:
        return tuple(
            str(getattr(decision, "initiative_id", decision))
            for decision in self.decisions
        )

    @property
    def districts(self) -> tuple[str, ...]:
        return tuple(
            str(district)
            for decision in self.decisions
            if (district := getattr(decision, "district", None)) is not None
        )


@dataclass(frozen=True)
class OptimizedScenario:
    candidate: CandidateScenario
    summary: ScenarioSummary
    reason: str

    @property
    def selected_initiatives(self) -> tuple[str, ...]:
        return self.candidate.selected_initiatives

    @property
    def districts(self) -> tuple[str, ...]:
        return self.candidate.districts

    @property
    def budget_used(self) -> float:
        return self.summary.budget_used

    @property
    def score(self) -> float:
        return self.summary.score

    @property
    def critical_metrics(self) -> tuple[str, ...]:
        return self.summary.critical_metrics


@dataclass(frozen=True)
class OptimizationResult:
    scenarios: tuple[OptimizedScenario, ...]
    checked_count: int
    valid_count: int
    max_checked: int
    truncated: bool
    reason: str


def find_best_scenarios(
    decision_options: Sequence[Sequence[str]],
    *,
    validator: Callable[[CandidateScenario], bool],
    simulator: Callable[[CandidateScenario], SimulationResult],
    scorer: Callable[[SimulationResult], float],
    top_n: int = 5,
    max_checked: int = 10_000,
) -> OptimizationResult:
    """Evaluate bounded valid combinations and return a transparent optimization result."""
    if top_n < 1:
        raise ValueError("top_n must be at least 1")
    if max_checked < 1:
        raise ValueError("max_checked must be at least 1")

    ranked: list[OptimizedScenario] = []
    checked_count = 0
    truncated = False
    for decisions in product(*decision_options):
        if checked_count >= max_checked:
            truncated = True
            break
        checked_count += 1
        candidate = CandidateScenario(tuple(decisions))
        if not validator(candidate):
            continue
        result = simulator(candidate)
        score = scorer(result)
        summary = summarize_scenario(
            " / ".join(candidate.selected_initiatives), result, score
        )
        reason = (
            f"Score {score:.2f}; budget {summary.budget_used:g}; "
            f"critical indicators: {summary.critical_count}."
        )
        ranked.append(OptimizedScenario(candidate, summary, reason))

    ranked.sort(key=lambda item: (-item.score, item.budget_used, item.selected_initiatives))
    scenarios = tuple(ranked[:top_n])
    if not scenarios:
        reason = "No valid scenarios found within the configured search limit."
    elif truncated:
        reason = f"Search limit reached after checking {checked_count} scenarios."
    else:
        reason = f"Checked all {checked_count} possible scenarios."
    return OptimizationResult(
        scenarios=scenarios,
        checked_count=checked_count,
        valid_count=len(ranked),
        max_checked=max_checked,
        truncated=truncated,
        reason=reason,
    )
