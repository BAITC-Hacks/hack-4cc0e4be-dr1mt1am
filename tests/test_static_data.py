"""Static specification checks, independent of future simulation behavior."""

import unittest
from dataclasses import FrozenInstanceError
from math import fsum

from engine import constants
from engine.data import (
    DIRECTION_WEIGHTS, DISTRICTS, INCOMPATIBILITIES, INDICATORS,
    INDICATOR_WEIGHTS, INITIATIVES, POPULATION_SHARES, SYNERGIES,
)
from engine.models import Direction, InitiativeType


INDICATOR_ORDER = ("T1", "T2", "E1", "E2", "S1", "S2", "B1", "B2", "C1", "C2")


class StaticDataTests(unittest.TestCase):
    def test_district_count_and_names(self):
        self.assertEqual(len(DISTRICTS), 5)
        self.assertEqual(set(DISTRICTS), {"Esil", "Almaty", "Saryarka", "Baikonur", "Nura"})
        for name, district in DISTRICTS.items():
            self.assertEqual(name, district.name)

    def test_population_shares(self):
        self.assertEqual(dict(POPULATION_SHARES), {
            "Esil": 0.27, "Almaty": 0.24, "Saryarka": 0.20,
            "Baikonur": 0.13, "Nura": 0.16,
        })
        self.assertAlmostEqual(fsum(POPULATION_SHARES.values()), 1.0)
        for name, district in DISTRICTS.items():
            self.assertEqual(district.population_share, POPULATION_SHARES[name])

    def test_all_baseline_values_match_specification(self):
        expected = {
            "Esil": ((45, 62, 68, 72, 48, 55, 78, 60, 75, 70), 62.99),
            "Almaty": ((40, 75, 50, 55, 60, 65, 62, 52, 50, 60), 57.06),
            "Saryarka": ((50, 70, 42, 40, 62, 68, 58, 55, 45, 55), 54.65),
            "Baikonur": ((52, 68, 55, 50, 58, 60, 52, 58, 55, 58), 56.63),
            "Nura": ((55, 40, 45, 65, 38, 35, 55, 50, 60, 50), 49.18),
        }
        for name, (values, supplied_score) in expected.items():
            with self.subTest(district=name):
                district = DISTRICTS[name]
                self.assertEqual(dict(district.baseline_indicators), dict(zip(INDICATOR_ORDER, values)))
                self.assertEqual(district.baseline_district_score, supplied_score)

    def test_baseline_indicator_coverage_and_range(self):
        for district in DISTRICTS.values():
            self.assertEqual(set(district.baseline_indicators), set(INDICATORS))
            for indicator, value in district.baseline_indicators.items():
                with self.subTest(district=district.name, indicator=indicator):
                    self.assertGreaterEqual(value, 0)
                    self.assertLessEqual(value, 100)

    def test_district_profiles(self):
        self.assertEqual({name: district.profile for name, district in DISTRICTS.items()}, {
            "Esil": "wealthier district, but bridge congestion and overcrowded schools.",
            "Almaty": "old utility infrastructure and traffic congestion.",
            "Saryarka": "smog caused by private-sector heating and weak greenery.",
            "Baikonur": "balanced middle district with no extreme weaknesses.",
            "Nura": "main underperformer in social infrastructure and public transport.",
        })

    def test_indicator_weights(self):
        self.assertEqual(dict(INDICATOR_WEIGHTS), dict(zip(
            INDICATOR_ORDER, (0.10, 0.10, 0.09, 0.11, 0.11, 0.11, 0.09, 0.09, 0.10, 0.10),
        )))
        self.assertAlmostEqual(fsum(INDICATOR_WEIGHTS.values()), 1.0)
        self.assertEqual(dict(DIRECTION_WEIGHTS), {
            Direction.TRANSPORT: 0.20, Direction.ECOLOGY: 0.20,
            Direction.SOCIAL: 0.22, Direction.SAFETY: 0.18, Direction.SERVICES: 0.20,
        })
        for direction, total_weight in DIRECTION_WEIGHTS.items():
            self.assertAlmostEqual(fsum(
                item.weight for item in INDICATORS.values() if item.direction == direction
            ), total_weight)

    def test_indicator_metadata(self):
        expected = {
            "T1": ("Transport", "Road congestion relief", "no peak-hour traffic congestion"),
            "T2": ("Transport", "Public transport accessibility",
                   "all residents within 500 m of a stop with service interval <= 10 minutes"),
            "E1": ("Ecology", "Greenery", ">=20 square meters of greenery per resident"),
            "E2": ("Ecology", "Air quality", "winter AQI <= 50"),
            "S1": ("Social", "Schools and kindergartens", "full normative demand covered, no second shift"),
            "S2": ("Social", "Clinics and primary healthcare", "full per-capita standard achieved"),
            "B1": ("Safety", "Street safety", "lighting and cameras everywhere, minimum incidents"),
            "B2": ("Safety", "Road safety", "minimum injury-related traffic accidents"),
            "C1": ("Services", "Utility reliability", "no heating/water accidents during the year"),
            "C2": ("Services", "Resident request resolution speed", "all resident requests resolved on time"),
        }
        self.assertEqual(set(INDICATORS), set(expected))
        for indicator_id, values in expected.items():
            with self.subTest(indicator=indicator_id):
                item = INDICATORS[indicator_id]
                self.assertEqual(item.id, indicator_id)
                self.assertEqual((item.direction.value, item.name, item.description_at_100), values)
                self.assertEqual(item.weight, INDICATOR_WEIGHTS[indicator_id])
                self.assertTrue(item.higher_is_better)
                self.assertEqual(item.description_at_0, "chronic smog" if indicator_id == "E2" else None)

    def test_initiative_count_and_unique_ids(self):
        expected_ids = {f"M{number}" for number in range(1, 15)}
        ids = [initiative.id for initiative in INITIATIVES.values()]
        self.assertEqual(len(INITIATIVES), 14)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), expected_ids)
        self.assertEqual(set(INITIATIVES), expected_ids)
        for initiative_id, initiative in INITIATIVES.items():
            self.assertEqual(initiative_id, initiative.id)

    def test_every_initiative_cost_and_lag(self):
        expected = {
            "M1": (18, 2), "M2": (22, 2), "M3": (30, 4), "M4": (15, 2),
            "M5": (25, 3), "M6": (20, 4), "M7": (24, 3), "M8": (20, 3),
            "M9": (10, 1), "M10": (12, 1), "M11": (10, 1), "M12": (14, 1),
            "M13": (28, 4), "M14": (16, 1),
        }
        self.assertEqual({key: (item.cost, item.lag) for key, item in INITIATIVES.items()}, expected)

    def test_initiative_names_directions_and_types(self):
        expected = {
            "M1": ("Dedicated bus lanes", "Transport", "District"),
            "M2": ("Smart traffic lights / adaptive traffic management", "Transport", "City"),
            "M3": ("LRT line / expansion", "Transport", "District"),
            "M4": ("Park / public square", "Ecology", "District"),
            "M5": ("Convert private-sector heating to clean fuel", "Ecology", "District"),
            "M6": ("City greenery and windbreak program", "Ecology", "City"),
            "M7": ("School + kindergarten modular construction", "Social", "District"),
            "M8": ("Family health center / clinic", "Social", "District"),
            "M9": ("Courtyard sports hubs", "Social", "District"),
            "M10": ("Lighting and cameras / Safe City expansion", "Safety", "District"),
            "M11": ("Safe crossings and school zones", "Safety", "District"),
            "M12": ("Unified digital resident request platform", "Services", "City"),
            "M13": ("Heating and water network modernization", "Services", "District"),
            "M14": ("Emergency utility teams + early warning", "Services", "City"),
        }
        self.assertEqual({
            key: (item.name, item.direction.value, item.type.value)
            for key, item in INITIATIVES.items()
        }, expected)

    def test_full_unscaled_initiative_effects(self):
        expected = {
            "M1": {"T1": 6, "T2": 9}, "M2": {"T1": 4, "B2": 3},
            "M3": {"T1": 16, "T2": 20, "E2": 4}, "M4": {"E1": 12, "E2": 3, "B1": 2},
            "M5": {"E2": 14, "C1": 4}, "M6": {"E1": 5, "E2": 3},
            "M7": {"S1": 16}, "M8": {"S2": 14}, "M9": {"S1": 3, "S2": 3, "B1": 3},
            "M10": {"B1": 12, "B2": 2}, "M11": {"B2": 12, "T1": -2},
            "M12": {"C2": 5}, "M13": {"C1": 18, "E2": 2}, "M14": {"C1": 5, "C2": 2},
        }
        for initiative_id, effects in expected.items():
            with self.subTest(initiative=initiative_id):
                actual = INITIATIVES[initiative_id].effects
                self.assertEqual(len(actual), len(effects))
                self.assertEqual({effect.indicator: effect.delta for effect in actual}, effects)
                self.assertTrue(all(effect.indicator in INDICATORS for effect in actual))

    def test_synergy_definitions_and_target_ownership(self):
        self.assertEqual(len(SYNERGIES), 3)
        self.assertEqual({
            (item.first_initiative_id, item.second_initiative_id,
             tuple((bonus.indicator, bonus.delta) for bonus in item.bonuses))
            for item in SYNERGIES
        }, {
            ("M1", "M2", (("T1", 2),)),
            ("M10", "M12", (("B1", 2),)),
            ("M5", "M6", (("E2", 2),)),
        })
        for synergy in SYNERGIES:
            self.assertEqual(INITIATIVES[synergy.first_initiative_id].type, InitiativeType.DISTRICT)
            self.assertIn(synergy.second_initiative_id, INITIATIVES)
            for bonus in synergy.bonuses:
                self.assertIn(bonus.indicator, INDICATORS)

    def test_incompatibility_definitions_and_scopes(self):
        self.assertEqual(len(INCOMPATIBILITIES), 3)
        self.assertEqual({
            (item.first_initiative_id, item.second_initiative_id, item.scope.value)
            for item in INCOMPATIBILITIES
        }, {
            ("M1", "M3", "scenario"),
            ("M4", "M7", "same_district"),
            ("M5", "M13", "same_district"),
        })
        for item in INCOMPATIBILITIES:
            self.assertIn(item.first_initiative_id, INITIATIVES)
            self.assertIn(item.second_initiative_id, INITIATIVES)

    def test_simulation_constants(self):
        self.assertEqual(constants.BUDGET, 100)
        self.assertEqual(constants.HORIZON_QUARTERS, 8)
        self.assertEqual(constants.REQUIRED_DECISION_COUNT, 5)
        self.assertEqual(constants.MAX_INITIATIVES_PER_DIRECTION, 2)
        self.assertEqual(constants.INDICATOR_MIN, 0)
        self.assertEqual(constants.INDICATOR_MAX, 100)
        self.assertEqual(constants.CRITICAL_THRESHOLD, 40)

    def test_shared_catalog_and_baselines_cannot_be_mutated(self):
        for mapping in (DISTRICTS, INITIATIVES, INDICATORS, INDICATOR_WEIGHTS,
                        POPULATION_SHARES, DIRECTION_WEIGHTS):
            key = next(iter(mapping))
            with self.assertRaises(TypeError):
                mapping[key] = mapping[key]
        with self.assertRaises(TypeError):
            DISTRICTS["Nura"].baseline_indicators["S1"] = 100
        with self.assertRaises(FrozenInstanceError):
            INITIATIVES["M1"].cost = 0
        with self.assertRaises(FrozenInstanceError):
            INITIATIVES["M1"].effects[0].delta = 100
        self.assertIsInstance(INITIATIVES["M1"].effects, tuple)
        self.assertIsInstance(SYNERGIES, tuple)
        self.assertIsInstance(INCOMPATIBILITIES, tuple)


if __name__ == "__main__":
    unittest.main()
