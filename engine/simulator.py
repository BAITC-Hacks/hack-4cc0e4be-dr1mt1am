"""Deterministic indicator effects; validation and scoring remain separate layers."""

from collections.abc import Sequence

from . import scoring
from .constants import HORIZON_QUARTERS, INDICATOR_MAX, INDICATOR_MIN
from .data import DISTRICTS, INITIATIVES, SYNERGIES
from .models import (
    Decision, DistrictIndicators, DistrictName, IndicatorId, InitiativeType,
    SimulationResult, TriggeredSynergy,
)
from .validator import validate_scenario


def simulate_scenario(decisions: Sequence[Decision]) -> SimulationResult:
    """Validate first, then calculate independent before/after snapshots and scores."""
    decisions = tuple(decisions)
    validation = validate_scenario(decisions)
    if not validation.valid:
        return SimulationResult(
            valid=False,
            validation=validation,
            budget_used=validation.budget_used,
            budget_remaining=validation.budget_remaining,
        )

    before = baseline_indicators()
    after = {district: dict(values) for district, values in before.items()}
    _apply_effects(decisions, after)
    triggered = _apply_synergies(decisions, after)
    after = clip_indicators(after)

    scores_before = scoring.calculate_district_scores(before)
    scores_after = scoring.calculate_district_scores(after)
    d_avg_before = scoring.calculate_d_avg(scores_before)
    d_avg_after = scoring.calculate_d_avg(scores_after)
    minimum_before = scoring.minimum_district_score(scores_before)
    minimum_after = scoring.minimum_district_score(scores_after)
    n_crit_before = scoring.count_critical_indicators(before)
    n_crit_after = scoring.count_critical_indicators(after)
    score_before = scoring.calculate_final_score(d_avg_before, minimum_before, n_crit_before)
    score_after = scoring.calculate_final_score(d_avg_after, minimum_after, n_crit_after)

    return SimulationResult(
        valid=True,
        validation=validation,
        budget_used=validation.budget_used,
        budget_remaining=validation.budget_remaining,
        indicators_before=before,
        indicators_after=after,
        district_scores_before=scores_before,
        district_scores_after=scores_after,
        d_avg_before=d_avg_before,
        d_avg_after=d_avg_after,
        weakest_district_before=scoring.weakest_district(scores_before),
        weakest_district_after=scoring.weakest_district(scores_after),
        min_district_score_before=minimum_before,
        min_district_score_after=minimum_after,
        n_crit_before=n_crit_before,
        n_crit_after=n_crit_after,
        score_before=score_before,
        score_after=score_after,
        score_delta=score_after - score_before,
        triggered_synergies=triggered,
    )


def baseline_indicators() -> dict[DistrictName, dict[IndicatorId, float]]:
    """Return a fresh, independent snapshot on every call."""
    return {
        name: dict(district.baseline_indicators)
        for name, district in DISTRICTS.items()
    }


def realized_fraction(lag: int) -> float:
    return (HORIZON_QUARTERS - lag) / HORIZON_QUARTERS


def clip_indicators(indicators: DistrictIndicators) -> dict[DistrictName, dict[IndicatorId, float]]:
    """Clip only after all deltas have been accumulated, without changing input."""
    return {
        district: {
            key: min(INDICATOR_MAX, max(INDICATOR_MIN, value))
            for key, value in values.items()
        }
        for district, values in indicators.items()
    }


def _apply_effects(
    decisions: Sequence[Decision],
    indicators: dict[DistrictName, dict[IndicatorId, float]],
) -> None:
    """Apply ordinary effects to a private snapshot of an already-valid scenario."""
    for decision in sorted(decisions, key=lambda item: item.initiative_id):
        initiative = INITIATIVES[decision.initiative_id]
        if initiative.type == InitiativeType.CITY:
            targets = tuple(DISTRICTS)
        else:
            assert decision.district is not None  # Guaranteed by validate_scenario.
            targets = (decision.district,)
        fraction = realized_fraction(initiative.lag)
        for district in targets:
            for effect in initiative.effects:
                indicators[district][effect.indicator] += effect.delta * fraction


def _apply_synergies(
    decisions: Sequence[Decision],
    indicators: dict[DistrictName, dict[IndicatorId, float]],
) -> tuple[TriggeredSynergy, ...]:
    """Apply each catalog synergy once, targeting its first member's district."""
    selected = {decision.initiative_id: decision for decision in decisions}
    triggered = []
    for synergy in SYNERGIES:
        if (synergy.first_initiative_id not in selected
                or synergy.second_initiative_id not in selected):
            continue
        district = selected[synergy.first_initiative_id].district
        assert district is not None  # Synergy owners are validated district initiatives.
        for bonus in synergy.bonuses:
            indicators[district][bonus.indicator] += bonus.delta
        triggered.append(TriggeredSynergy(synergy, district))
    return tuple(triggered)
