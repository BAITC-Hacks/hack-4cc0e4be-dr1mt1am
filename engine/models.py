"""Typed domain records. Scenario validation belongs to the future validator."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Mapping


IndicatorId = Literal["T1", "T2", "E1", "E2", "S1", "S2", "B1", "B2", "C1", "C2"]
DistrictName = Literal["Esil", "Almaty", "Saryarka", "Baikonur", "Nura"]
InitiativeId = Literal[
    "M1", "M2", "M3", "M4", "M5", "M6", "M7",
    "M8", "M9", "M10", "M11", "M12", "M13", "M14",
]


class Direction(str, Enum):
    TRANSPORT = "Transport"
    ECOLOGY = "Ecology"
    SOCIAL = "Social"
    SAFETY = "Safety"
    SERVICES = "Services"


class InitiativeType(str, Enum):
    DISTRICT = "District"
    CITY = "City"


class IncompatibilityScope(str, Enum):
    SCENARIO = "scenario"
    SAME_DISTRICT = "same_district"


@dataclass(frozen=True)
class IndicatorMetadata:
    id: IndicatorId
    direction: Direction
    name: str
    weight: float
    description_at_100: str
    description_at_0: str | None = None
    higher_is_better: bool = True


@dataclass(frozen=True)
class District:
    name: DistrictName
    population_share: float
    baseline_indicators: Mapping[IndicatorId, float]
    profile: str
    baseline_district_score: float  # Supplied reference value, not calculated here.


@dataclass(frozen=True)
class InitiativeEffect:
    """An unscaled indicator delta; also used for fixed synergy bonuses."""

    indicator: IndicatorId
    delta: float


@dataclass(frozen=True)
class Initiative:
    id: InitiativeId
    direction: Direction
    name: str
    type: InitiativeType
    cost: int
    lag: int  # Quarters; effects remain unscaled in this record.
    effects: tuple[InitiativeEffect, ...]


@dataclass(frozen=True)
class Decision:
    """A selection to be validated later; city scope is represented by None."""

    initiative_id: InitiativeId
    district: DistrictName | None = None


@dataclass(frozen=True)
class Synergy:
    """Fixed bonuses target the district of first_initiative_id in this pair."""

    first_initiative_id: InitiativeId
    second_initiative_id: InitiativeId
    bonuses: tuple[InitiativeEffect, ...]


@dataclass(frozen=True)
class Incompatibility:
    first_initiative_id: InitiativeId
    second_initiative_id: InitiativeId
    scope: IncompatibilityScope
