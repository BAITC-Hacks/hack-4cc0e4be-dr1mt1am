"""Independent JSON snapshots, preserving engine precision."""

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

from engine import scoring
from engine.constants import (
    BUDGET, CRITICAL_THRESHOLD, HORIZON_QUARTERS,
    MAX_INITIATIVES_PER_DIRECTION, REQUIRED_DECISION_COUNT,
)
from engine.data import (
    DIRECTION_WEIGHTS, DISTRICTS, INCOMPATIBILITIES, INDICATORS,
    INDICATOR_WEIGHTS, INITIATIVES, POPULATION_SHARES, SYNERGIES,
)
from engine.models import SimulationResult
from engine.simulator import baseline_indicators


def json_snapshot(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: json_snapshot(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {json_snapshot(key): json_snapshot(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_snapshot(item) for item in value]
    return value


def simulation_response(result: SimulationResult) -> dict[str, Any]:
    if not result.valid:
        return {
            "valid": False, "errors": json_snapshot(result.validation.errors),
            "budget_used": result.budget_used, "budget_remaining": result.budget_remaining,
        }
    return json_snapshot(result)


def catalog_response() -> dict[str, Any]:
    indicators = baseline_indicators()
    scores = scoring.calculate_district_scores(indicators)
    critical = scoring.count_critical_indicators(indicators)
    baseline_score = scoring.calculate_final_score(
        scoring.calculate_d_avg(scores), scoring.minimum_district_score(scores), critical,
    )
    return json_snapshot({
        "budget": BUDGET, "required_decisions": REQUIRED_DECISION_COUNT,
        "max_per_direction": MAX_INITIATIVES_PER_DIRECTION, "horizon": HORIZON_QUARTERS,
        "critical_threshold": CRITICAL_THRESHOLD,
        "indicator_metadata": INDICATORS, "indicator_weights": INDICATOR_WEIGHTS,
        "direction_weights": DIRECTION_WEIGHTS, "population_shares": POPULATION_SHARES,
        "baseline_indicators": indicators, "baseline_district_scores": scores,
        "baseline_score": baseline_score, "baseline_n_crit": critical,
        "weakest_district": scoring.weakest_district(scores),
        "districts": [
            {"id": name, "name": name, "populationShare": district.population_share,
             "score": scores[name], "indicators": indicators[name], "profile": district.profile}
            for name, district in DISTRICTS.items()
        ],
        "initiatives": [
            {"id": item.id, "name": item.name, "direction": item.direction, "type": item.type,
             "cost": item.cost, "lag": item.lag,
             "effects": [(effect.indicator, effect.delta) for effect in item.effects]}
            for item in INITIATIVES.values()
        ],
        "synergies": SYNERGIES, "incompatibilities": INCOMPATIBILITIES,
    })
