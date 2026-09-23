"""Numerical regressions for the pure scoring layer."""

import unittest
from math import nextafter

from engine.data import DISTRICTS, INDICATOR_WEIGHTS
from engine.scoring import (
    calculate_d_avg, calculate_district_score, calculate_district_scores, calculate_final_score,
    count_critical_indicators, minimum_district_score, weakest_district,
)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {
            name: dict(district.baseline_indicators)
            for name, district in DISTRICTS.items()
        }

    def test_baseline_district_scores(self):
        expected = {
            "Esil": 62.99, "Almaty": 57.06, "Saryarka": 54.65,
            "Baikonur": 56.63, "Nura": 49.18,
        }
        actual = calculate_district_scores(self.baseline)
        self.assertEqual(set(actual), set(expected))
        for district, score in expected.items():
            with self.subTest(district=district):
                self.assertAlmostEqual(actual[district], score, places=10)
                self.assertAlmostEqual(calculate_district_score(self.baseline[district]), score, places=10)

    def test_baseline_population_weighted_average(self):
        scores = calculate_district_scores(self.baseline)
        self.assertAlmostEqual(calculate_d_avg(scores), 56.8624, places=10)

    def test_baseline_final_score_regression(self):
        scores = calculate_district_scores(self.baseline)
        result = calculate_final_score(
            calculate_d_avg(scores), minimum_district_score(scores),
            count_critical_indicators(self.baseline),
        )
        self.assertAlmostEqual(result, 52.55768, places=10)

    def test_critical_penalty_subtracts_one_point_per_pair(self):
        self.assertAlmostEqual(calculate_final_score(60.0, 50.0, 0), 57.0)
        self.assertAlmostEqual(calculate_final_score(60.0, 50.0, 3), 54.0)

    def test_final_score_is_not_rounded_or_clipped(self):
        self.assertAlmostEqual(calculate_final_score(58.0776, 52.9625, 0), 56.54307, places=10)
        self.assertEqual(calculate_final_score(0.0, 0.0, 50), -50.0)

    def test_baseline_weakest_district_and_minimum(self):
        scores = calculate_district_scores(self.baseline)
        self.assertEqual(weakest_district(scores), "Nura")
        self.assertAlmostEqual(minimum_district_score(scores), 49.18, places=10)

    def test_baseline_critical_pairs(self):
        self.assertEqual(count_critical_indicators(self.baseline), 2)
        self.assertEqual({
            (district, indicator, value)
            for district, indicators in self.baseline.items()
            for indicator, value in indicators.items() if value < 40
        }, {("Nura", "S1", 38), ("Nura", "S2", 35)})

    def test_exactly_40_is_not_critical(self):
        indicators = {
            district: {indicator: 40.0 for indicator in INDICATOR_WEIGHTS}
            for district in DISTRICTS
        }
        self.assertEqual(count_critical_indicators(indicators), 0)

    def test_nearest_float_below_40_is_critical(self):
        indicators = {
            district: {indicator: 40.0 for indicator in INDICATOR_WEIGHTS}
            for district in DISTRICTS
        }
        indicators["Nura"]["S1"] = nextafter(40.0, 0.0)
        indicators["Esil"]["S1"] = nextafter(40.0, 0.0)
        self.assertEqual(count_critical_indicators(indicators), 2)

    def test_no_intermediate_rounding(self):
        values = {indicator: 0.0 for indicator in INDICATOR_WEIGHTS}
        values["E1"] = 0.123456789
        self.assertAlmostEqual(calculate_district_score(values), 0.01111111101, places=14)

    def test_scoring_does_not_mutate_input(self):
        before = {district: dict(values) for district, values in self.baseline.items()}
        scores = calculate_district_scores(self.baseline)
        calculate_d_avg(scores)
        weakest_district(scores)
        minimum_district_score(scores)
        count_critical_indicators(self.baseline)
        self.assertEqual(self.baseline, before)

    def test_equal_weakest_scores_have_stable_tie_break(self):
        first = {"Nura": 50.0, "Esil": 50.0, "Almaty": 60.0}
        second = dict(reversed(list(first.items())))
        self.assertEqual(weakest_district(first), "Esil")
        self.assertEqual(weakest_district(second), "Esil")

    def test_missing_indicator_is_not_assumed_zero(self):
        values = dict(self.baseline["Nura"])
        del values["S1"]
        with self.assertRaises(KeyError):
            calculate_district_score(values)


if __name__ == "__main__":
    unittest.main()
