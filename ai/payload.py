"""Serialize simulator facts, without recalculating scores, deltas, or budgets."""

from dataclasses import asdict
from typing import Any

from engine.data import INDICATORS
from engine.models import SimulationResult

from .models import InvalidSimulationError


def _presentation_copy(value: Any) -> Any:
    """Copy JSON data, rounding floats only at the LLM presentation boundary."""
    if isinstance(value, float):
        rounded = round(value, 2)
        return 0.0 if rounded == 0 else rounded
    if isinstance(value, dict):
        return {key: _presentation_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_presentation_copy(item) for item in value]
    return value


def build_analysis_payload(result: SimulationResult) -> dict[str, Any]:
    if not result.valid or not result.validation.valid or result.validation.errors:
        raise InvalidSimulationError("AI-анализ доступен только для валидного результата симуляции.")

    fact_fields = (
        "score_before", "score_after", "score_delta", "budget_used", "budget_remaining",
        "district_scores_before", "district_scores_after", "district_score_changes",
        "indicators_before", "indicators_after", "indicator_changes",
        "d_avg_before", "d_avg_after", "weakest_district_before", "weakest_district_after",
        "min_district_score_before", "min_district_score_after", "n_crit_before", "n_crit_after",
    )
    if any(getattr(result, name) is None for name in fact_fields) or not result.selected_initiatives:
        raise InvalidSimulationError("Результат симуляции неполный; выполните симуляцию заново.")

    payload = {name: getattr(result, name) for name in fact_fields}
    payload["selected_initiatives"] = [
        {
            "id": item.initiative.id,
            "name": item.initiative.name,
            "direction": item.initiative.direction.value,
            "type": item.initiative.type.value,
            "cost": item.initiative.cost,
            "target_district": item.decision.district,
        }
        for item in result.selected_initiatives
    ]
    payload["triggered_synergies"] = [
        {
            "initiative_ids": [item.synergy.first_initiative_id, item.synergy.second_initiative_id],
            "target_district": item.district,
            "bonuses": [asdict(bonus) for bonus in item.synergy.bonuses],
        }
        for item in result.triggered_synergies
    ]
    # Descriptions only: the catalog supplies vocabulary, not a second calculation.
    payload["indicator_metadata"] = {
        key: {"name": item.name, "direction": item.direction.value, "higher_is_better": item.higher_is_better}
        for key, item in INDICATORS.items()
    }
    return _presentation_copy(payload)
