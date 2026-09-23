"""Authoritative static data transcribed from docs/PROJECT_SPEC.md.

Effects are full, unscaled deltas. Synergies and incompatibilities are definitions
only. Read-only mappings and tuples protect the shared baseline and catalog.
"""

from types import MappingProxyType
from typing import Mapping

from .models import (
    Direction, District, DistrictName, Incompatibility, IncompatibilityScope,
    IndicatorId, IndicatorMetadata, Initiative, InitiativeEffect, InitiativeId,
    InitiativeType, Synergy,
)


INDICATORS: Mapping[IndicatorId, IndicatorMetadata] = MappingProxyType({
    "T1": IndicatorMetadata(
        "T1", Direction.TRANSPORT, "Road congestion relief", 0.10,
        "no peak-hour traffic congestion",
    ),
    "T2": IndicatorMetadata(
        "T2", Direction.TRANSPORT, "Public transport accessibility", 0.10,
        "all residents within 500 m of a stop with service interval <= 10 minutes",
    ),
    "E1": IndicatorMetadata(
        "E1", Direction.ECOLOGY, "Greenery", 0.09,
        ">=20 square meters of greenery per resident",
    ),
    "E2": IndicatorMetadata(
        "E2", Direction.ECOLOGY, "Air quality", 0.11,
        "winter AQI <= 50", "chronic smog",
    ),
    "S1": IndicatorMetadata(
        "S1", Direction.SOCIAL, "Schools and kindergartens", 0.11,
        "full normative demand covered, no second shift",
    ),
    "S2": IndicatorMetadata(
        "S2", Direction.SOCIAL, "Clinics and primary healthcare", 0.11,
        "full per-capita standard achieved",
    ),
    "B1": IndicatorMetadata(
        "B1", Direction.SAFETY, "Street safety", 0.09,
        "lighting and cameras everywhere, minimum incidents",
    ),
    "B2": IndicatorMetadata(
        "B2", Direction.SAFETY, "Road safety", 0.09,
        "minimum injury-related traffic accidents",
    ),
    "C1": IndicatorMetadata(
        "C1", Direction.SERVICES, "Utility reliability", 0.10,
        "no heating/water accidents during the year",
    ),
    "C2": IndicatorMetadata(
        "C2", Direction.SERVICES, "Resident request resolution speed", 0.10,
        "all resident requests resolved on time",
    ),
})

INDICATOR_WEIGHTS: Mapping[IndicatorId, float] = MappingProxyType({
    indicator_id: metadata.weight for indicator_id, metadata in INDICATORS.items()
})

DIRECTION_WEIGHTS: Mapping[Direction, float] = MappingProxyType({
    Direction.TRANSPORT: 0.20,
    Direction.ECOLOGY: 0.20,
    Direction.SOCIAL: 0.22,
    Direction.SAFETY: 0.18,
    Direction.SERVICES: 0.20,
})

DISTRICTS: Mapping[DistrictName, District] = MappingProxyType({
    "Esil": District(
        name="Esil", population_share=0.27,
        baseline_indicators=MappingProxyType({
            "T1": 45, "T2": 62, "E1": 68, "E2": 72, "S1": 48,
            "S2": 55, "B1": 78, "B2": 60, "C1": 75, "C2": 70,
        }),
        profile="wealthier district, but bridge congestion and overcrowded schools.",
        baseline_district_score=62.99,
    ),
    "Almaty": District(
        name="Almaty", population_share=0.24,
        baseline_indicators=MappingProxyType({
            "T1": 40, "T2": 75, "E1": 50, "E2": 55, "S1": 60,
            "S2": 65, "B1": 62, "B2": 52, "C1": 50, "C2": 60,
        }),
        profile="old utility infrastructure and traffic congestion.",
        baseline_district_score=57.06,
    ),
    "Saryarka": District(
        name="Saryarka", population_share=0.20,
        baseline_indicators=MappingProxyType({
            "T1": 50, "T2": 70, "E1": 42, "E2": 40, "S1": 62,
            "S2": 68, "B1": 58, "B2": 55, "C1": 45, "C2": 55,
        }),
        profile="smog caused by private-sector heating and weak greenery.",
        baseline_district_score=54.65,
    ),
    "Baikonur": District(
        name="Baikonur", population_share=0.13,
        baseline_indicators=MappingProxyType({
            "T1": 52, "T2": 68, "E1": 55, "E2": 50, "S1": 58,
            "S2": 60, "B1": 52, "B2": 58, "C1": 55, "C2": 58,
        }),
        profile="balanced middle district with no extreme weaknesses.",
        baseline_district_score=56.63,
    ),
    "Nura": District(
        name="Nura", population_share=0.16,
        baseline_indicators=MappingProxyType({
            "T1": 55, "T2": 40, "E1": 45, "E2": 65, "S1": 38,
            "S2": 35, "B1": 55, "B2": 50, "C1": 60, "C2": 50,
        }),
        profile="main underperformer in social infrastructure and public transport.",
        baseline_district_score=49.18,
    ),
})

POPULATION_SHARES: Mapping[DistrictName, float] = MappingProxyType({
    name: district.population_share for name, district in DISTRICTS.items()
})

INITIATIVES: Mapping[InitiativeId, Initiative] = MappingProxyType({
    "M1": Initiative(
        "M1", Direction.TRANSPORT, "Dedicated bus lanes", InitiativeType.DISTRICT,
        cost=18, lag=2,
        effects=(InitiativeEffect("T1", 6), InitiativeEffect("T2", 9)),
    ),
    "M2": Initiative(
        "M2", Direction.TRANSPORT, "Smart traffic lights / adaptive traffic management",
        InitiativeType.CITY, cost=22, lag=2,
        effects=(InitiativeEffect("T1", 4), InitiativeEffect("B2", 3)),
    ),
    "M3": Initiative(
        "M3", Direction.TRANSPORT, "LRT line / expansion", InitiativeType.DISTRICT,
        cost=30, lag=4,
        effects=(
            InitiativeEffect("T1", 16), InitiativeEffect("T2", 20),
            InitiativeEffect("E2", 4),
        ),
    ),
    "M4": Initiative(
        "M4", Direction.ECOLOGY, "Park / public square", InitiativeType.DISTRICT,
        cost=15, lag=2,
        effects=(
            InitiativeEffect("E1", 12), InitiativeEffect("E2", 3),
            InitiativeEffect("B1", 2),
        ),
    ),
    "M5": Initiative(
        "M5", Direction.ECOLOGY, "Convert private-sector heating to clean fuel",
        InitiativeType.DISTRICT, cost=25, lag=3,
        effects=(InitiativeEffect("E2", 14), InitiativeEffect("C1", 4)),
    ),
    "M6": Initiative(
        "M6", Direction.ECOLOGY, "City greenery and windbreak program",
        InitiativeType.CITY, cost=20, lag=4,
        effects=(InitiativeEffect("E1", 5), InitiativeEffect("E2", 3)),
    ),
    "M7": Initiative(
        "M7", Direction.SOCIAL, "School + kindergarten modular construction",
        InitiativeType.DISTRICT, cost=24, lag=3,
        effects=(InitiativeEffect("S1", 16),),
    ),
    "M8": Initiative(
        "M8", Direction.SOCIAL, "Family health center / clinic",
        InitiativeType.DISTRICT, cost=20, lag=3,
        effects=(InitiativeEffect("S2", 14),),
    ),
    "M9": Initiative(
        "M9", Direction.SOCIAL, "Courtyard sports hubs", InitiativeType.DISTRICT,
        cost=10, lag=1,
        effects=(
            InitiativeEffect("S1", 3), InitiativeEffect("S2", 3),
            InitiativeEffect("B1", 3),
        ),
    ),
    "M10": Initiative(
        "M10", Direction.SAFETY, "Lighting and cameras / Safe City expansion",
        InitiativeType.DISTRICT, cost=12, lag=1,
        effects=(InitiativeEffect("B1", 12), InitiativeEffect("B2", 2)),
    ),
    "M11": Initiative(
        "M11", Direction.SAFETY, "Safe crossings and school zones",
        InitiativeType.DISTRICT, cost=10, lag=1,
        effects=(InitiativeEffect("B2", 12), InitiativeEffect("T1", -2)),
    ),
    "M12": Initiative(
        "M12", Direction.SERVICES, "Unified digital resident request platform",
        InitiativeType.CITY, cost=14, lag=1,
        effects=(InitiativeEffect("C2", 5),),
    ),
    "M13": Initiative(
        "M13", Direction.SERVICES, "Heating and water network modernization",
        InitiativeType.DISTRICT, cost=28, lag=4,
        effects=(InitiativeEffect("C1", 18), InitiativeEffect("E2", 2)),
    ),
    "M14": Initiative(
        "M14", Direction.SERVICES, "Emergency utility teams + early warning",
        InitiativeType.CITY, cost=16, lag=1,
        effects=(InitiativeEffect("C1", 5), InitiativeEffect("C2", 2)),
    ),
})

SYNERGIES: tuple[Synergy, ...] = (
    Synergy("M1", "M2", (InitiativeEffect("T1", 2),)),
    Synergy("M10", "M12", (InitiativeEffect("B1", 2),)),
    Synergy("M5", "M6", (InitiativeEffect("E2", 2),)),
)

INCOMPATIBILITIES: tuple[Incompatibility, ...] = (
    Incompatibility("M1", "M3", IncompatibilityScope.SCENARIO),
    Incompatibility("M4", "M7", IncompatibilityScope.SAME_DISTRICT),
    Incompatibility("M5", "M13", IncompatibilityScope.SAME_DISTRICT),
)
