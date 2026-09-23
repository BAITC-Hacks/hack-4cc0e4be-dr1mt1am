"""Simulation constants from docs/PROJECT_SPEC.md; no rule execution."""

from typing import Final


BUDGET: Final[int] = 100
HORIZON_QUARTERS: Final[int] = 8
REQUIRED_DECISION_COUNT: Final[int] = 5
MAX_INITIATIVES_PER_DIRECTION: Final[int] = 2
INDICATOR_MIN: Final[int] = 0
INDICATOR_MAX: Final[int] = 100
CRITICAL_THRESHOLD: Final[int] = 40  # Strictly less than this value is critical.
CITY_AVERAGE_WEIGHT: Final[float] = 0.7
WEAKEST_DISTRICT_WEIGHT: Final[float] = 0.3
CRITICAL_PENALTY: Final[float] = 1.0
