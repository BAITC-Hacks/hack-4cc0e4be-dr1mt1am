"""Pure score components using the authoritative indicator and population weights."""

from math import fsum

from .constants import (
    CITY_AVERAGE_WEIGHT, CRITICAL_PENALTY, CRITICAL_THRESHOLD,
    WEAKEST_DISTRICT_WEIGHT,
)
from .data import INDICATOR_WEIGHTS, POPULATION_SHARES
from .models import DistrictIndicators, DistrictName, DistrictScores, IndicatorValues


def calculate_district_score(indicators: IndicatorValues) -> float:
    """Calculate a district's weighted indicators without rounding."""
    return fsum(weight * indicators[key] for key, weight in INDICATOR_WEIGHTS.items())


def calculate_district_scores(indicators: DistrictIndicators) -> dict[DistrictName, float]:
    return {
        district: calculate_district_score(indicators[district])
        for district in sorted(indicators)
    }


def calculate_d_avg(district_scores: DistrictScores) -> float:
    return fsum(
        population_share * district_scores[district]
        for district, population_share in POPULATION_SHARES.items()
    )


def minimum_district_score(district_scores: DistrictScores) -> float:
    return min(district_scores.values())


def weakest_district(district_scores: DistrictScores) -> DistrictName:
    """Break equal-score ties alphabetically by the existing district identifier."""
    return min(district_scores, key=lambda district: (district_scores[district], district))


def count_critical_indicators(indicators: DistrictIndicators) -> int:
    """Exactly 40 is not critical; inspect every district/indicator pair."""
    return sum(
        value < CRITICAL_THRESHOLD
        for district_indicators in indicators.values()
        for value in district_indicators.values()
    )


def calculate_final_score(d_avg: float, min_district_score: float, n_crit: int) -> float:
    """Apply the critical penalty by subtraction, as explicitly confirmed by the user."""
    return (
        CITY_AVERAGE_WEIGHT * d_avg
        + WEAKEST_DISTRICT_WEIGHT * min_district_score
        - CRITICAL_PENALTY * n_crit
    )
