"""Deterministic indicator simulation and public pipeline regressions."""

import unittest
from contextlib import ExitStack
from dataclasses import asdict
from itertools import permutations
from unittest.mock import patch

from engine import data
from engine.models import Decision
from engine.simulator import (
    baseline_indicators, clip_indicators, realized_fraction, simulate_scenario,
)
from engine.validator import validate_scenario


REFERENCE = (
    Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M10", "Nura"),
    Decision("M12"), Decision("M5", "Saryarka"),
)


class IndicatorSimulationTests(unittest.TestCase):
    def apply_valid_scenario(self, decisions):
        result = simulate_scenario(decisions)
        self.assertTrue(result.valid, result.validation.errors)
        return result.indicators_after, result.triggered_synergies

    def test_reference_indicator_effects(self):
        after, triggered = self.apply_valid_scenario(REFERENCE)
        expected = baseline_indicators()
        expected["Nura"].update({"S1": 48.0, "S2": 43.75, "B1": 67.5, "B2": 51.75})
        expected["Saryarka"].update({"E2": 48.75, "C1": 47.5})
        for district in expected:
            expected[district]["C2"] += 4.375
        self.assertEqual(after, expected)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].district, "Nura")
        self.assertEqual(triggered[0].synergy.first_initiative_id, "M10")
        self.assertEqual(triggered[0].synergy.second_initiative_id, "M12")

    def test_city_effect_reaches_all_five_districts(self):
        after, _ = self.apply_valid_scenario(REFERENCE)
        for district in data.DISTRICTS:
            self.assertEqual(after[district]["C2"], data.DISTRICTS[district].baseline_indicators["C2"] + 4.375)

    def test_district_effect_does_not_reach_other_districts(self):
        after, _ = self.apply_valid_scenario(REFERENCE)
        self.assertEqual(after["Nura"]["S1"], 48.0)
        for district in data.DISTRICTS:
            if district != "Nura":
                self.assertEqual(after[district]["S1"], data.DISTRICTS[district].baseline_indicators["S1"])

    def test_realized_fractions_for_all_catalog_lags(self):
        for lag, expected in ((1, 0.875), (2, 0.75), (3, 0.625), (4, 0.5)):
            with self.subTest(lag=lag):
                self.assertEqual(realized_fraction(lag), expected)

    def test_lag_two_effects_and_m1_m2_fixed_synergy(self):
        after, triggered = self.apply_valid_scenario((
            Decision("M1", "Nura"), Decision("M2"), Decision("M4", "Esil"),
            Decision("M9", "Almaty"), Decision("M14"),
        ))
        self.assertEqual(after["Nura"]["T1"], 55 + 4.5 + 3 + 2)
        self.assertEqual(after["Nura"]["T2"], 40 + 6.75)
        for district in data.DISTRICTS:
            if district != "Nura":
                self.assertEqual(after[district]["T1"], data.DISTRICTS[district].baseline_indicators["T1"] + 3)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].district, "Nura")

    def test_m5_m6_fixed_synergy(self):
        after, triggered = self.apply_valid_scenario((
            Decision("M5", "Saryarka"), Decision("M6"), Decision("M9", "Nura"),
            Decision("M11", "Esil"), Decision("M12"),
        ))
        self.assertEqual(after["Saryarka"]["E2"], 40 + 8.75 + 1.5 + 2)
        self.assertEqual(after["Saryarka"]["E1"], 42 + 2.5)
        self.assertEqual(after["Nura"]["E2"], 65 + 1.5)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].district, "Saryarka")

    def test_lag_four_district_effect(self):
        after, _ = self.apply_valid_scenario((
            Decision("M3", "Nura"), Decision("M7", "Nura"), Decision("M6"),
            Decision("M10", "Esil"), Decision("M12"),
        ))
        self.assertEqual(after["Nura"]["T1"], 55 + 8)
        self.assertEqual(after["Nura"]["T2"], 40 + 10)
        self.assertEqual(after["Nura"]["E2"], 65 + 2 + 1.5)

    def test_negative_m11_effect_is_lag_scaled(self):
        after, _ = self.apply_valid_scenario((
            Decision("M11", "Esil"), Decision("M4", "Nura"), Decision("M9", "Nura"),
            Decision("M12"), Decision("M14"),
        ))
        self.assertEqual(after["Esil"]["T1"], 43.25)
        self.assertEqual(after["Esil"]["B2"], 70.5)

    def test_no_synergy_without_both_members(self):
        _, triggered = self.apply_valid_scenario((
            Decision("M1", "Nura"), Decision("M4", "Esil"), Decision("M9", "Almaty"),
            Decision("M10", "Nura"), Decision("M14"),
        ))
        self.assertEqual(triggered, ())

    def test_clip_upper_and_lower_limits_without_mutation(self):
        before = baseline_indicators()
        before["Nura"]["S1"] = 105.125
        before["Esil"]["T1"] = -1.75
        before["Esil"]["T2"] = 99.9999
        after = clip_indicators(before)
        self.assertEqual(after["Nura"]["S1"], 100)
        self.assertEqual(after["Esil"]["T1"], 0)
        self.assertEqual(after["Esil"]["T2"], 99.9999)
        self.assertEqual(before["Nura"]["S1"], 105.125)
        self.assertEqual(before["Esil"]["T1"], -1.75)

    def test_baseline_snapshots_do_not_share_nested_maps(self):
        first, second = baseline_indicators(), baseline_indicators()
        first["Nura"]["S1"] = 100
        self.assertEqual(second["Nura"]["S1"], 38)
        self.assertEqual(data.DISTRICTS["Nura"].baseline_indicators["S1"], 38)

    def test_effects_and_synergies_do_not_mutate_static_data(self):
        before = repr((data.DISTRICTS, data.INITIATIVES, data.SYNERGIES))
        self.apply_valid_scenario(REFERENCE)
        self.assertEqual(repr((data.DISTRICTS, data.INITIATIVES, data.SYNERGIES)), before)

    def test_effects_and_synergies_are_order_invariant(self):
        expected = self.apply_valid_scenario(REFERENCE)
        for ordering in permutations(REFERENCE):
            self.assertEqual(self.apply_valid_scenario(ordering), expected)

    def test_m13_lag_four_effects(self):
        after, _ = self.apply_valid_scenario((
            Decision("M13", "Almaty"), Decision("M1", "Nura"), Decision("M4", "Esil"),
            Decision("M9", "Nura"), Decision("M10", "Nura"),
        ))
        self.assertEqual(after["Almaty"]["C1"], 59.0)
        self.assertEqual(after["Almaty"]["E2"], 56.0)
        for district in data.DISTRICTS:
            if district != "Almaty":
                self.assertEqual(after[district]["C1"], data.DISTRICTS[district].baseline_indicators["C1"])

    def test_m14_city_effects(self):
        after, _ = self.apply_valid_scenario((
            Decision("M1", "Nura"), Decision("M4", "Esil"), Decision("M9", "Almaty"),
            Decision("M10", "Nura"), Decision("M14"),
        ))
        for district in data.DISTRICTS:
            before = data.DISTRICTS[district].baseline_indicators
            self.assertEqual(after[district]["C1"], before["C1"] + 4.375)
            self.assertEqual(after[district]["C2"], before["C2"] + 1.75)

    def test_clipping_occurs_after_both_positive_and_negative_effects(self):
        synthetic = baseline_indicators()
        synthetic["Esil"]["T1"] = 99.0
        with patch("engine.simulator.baseline_indicators", return_value=synthetic):
            result = simulate_scenario((
                Decision("M1", "Esil"), Decision("M11", "Esil"), Decision("M4", "Nura"),
                Decision("M9", "Almaty"), Decision("M12"),
            ))
        self.assertTrue(result.valid)
        # 99 + 4.5 - 1.75 = 101.75 -> 100, not 98.25 from premature clipping.
        self.assertEqual(result.indicators_after["Esil"]["T1"], 100)
        self.assertEqual(synthetic["Esil"]["T1"], 99.0)

    def test_synergy_is_clipped_before_scoring(self):
        synthetic = baseline_indicators()
        synthetic["Nura"]["B1"] = 89.0
        with patch("engine.simulator.baseline_indicators", return_value=synthetic):
            result = simulate_scenario(REFERENCE)
        self.assertEqual(result.indicators_after["Nura"]["B1"], 100)
        self.assertAlmostEqual(result.district_scores_after["Nura"], 55.8875, places=10)

    def test_negative_effect_is_clipped_at_zero_before_scoring(self):
        synthetic = baseline_indicators()
        synthetic["Esil"]["T1"] = 0.5
        with patch("engine.simulator.baseline_indicators", return_value=synthetic):
            result = simulate_scenario((
                Decision("M11", "Esil"), Decision("M4", "Nura"), Decision("M9", "Nura"),
                Decision("M12"), Decision("M14"),
            ))
        self.assertTrue(result.valid)
        self.assertEqual(result.indicators_after["Esil"]["T1"], 0)
        # Original 62.99 minus T1's 4.5, plus B2's .945, C1's .4375, C2's .6125.
        self.assertAlmostEqual(result.district_scores_after["Esil"], 60.485, places=10)


class SimulationPipelineTests(unittest.TestCase):
    def test_reference_scenario_full_regression(self):
        result = simulate_scenario(REFERENCE)
        self.assertTrue(result.valid)
        self.assertEqual(result.validation, validate_scenario(REFERENCE))
        self.assertEqual((result.budget_used, result.budget_remaining), (95, 5))
        self.assertEqual(result.indicators_before, baseline_indicators())
        expected_before = {
            "Esil": 62.99, "Almaty": 57.06, "Saryarka": 54.65,
            "Baikonur": 56.63, "Nura": 49.18,
        }
        expected_after = {
            "Esil": 63.4275, "Almaty": 57.4975, "Saryarka": 56.3,
            "Baikonur": 57.0675, "Nura": 52.9625,
        }
        for district in expected_before:
            self.assertAlmostEqual(result.district_scores_before[district], expected_before[district], places=10)
            self.assertAlmostEqual(result.district_scores_after[district], expected_after[district], places=10)
        self.assertAlmostEqual(result.d_avg_before, 56.8624, places=10)
        self.assertAlmostEqual(result.d_avg_after, 58.0776, places=10)
        self.assertEqual(result.weakest_district_before, "Nura")
        self.assertEqual(result.weakest_district_after, "Nura")
        self.assertAlmostEqual(result.min_district_score_before, 49.18, places=10)
        self.assertAlmostEqual(result.min_district_score_after, 52.9625, places=10)
        self.assertEqual(result.n_crit_before, 2)
        self.assertEqual(result.n_crit_after, 0)
        self.assertAlmostEqual(result.score_before, 52.55768, places=10)
        self.assertAlmostEqual(result.score_after, 56.54307, places=10)
        self.assertAlmostEqual(result.score_delta, 3.98539, places=10)

    def test_all_120_reference_permutations_return_identical_full_results(self):
        expected = simulate_scenario(REFERENCE)
        count = 0
        for ordering in permutations(REFERENCE):
            self.assertEqual(simulate_scenario(ordering), expected)
            count += 1
        self.assertEqual(count, 120)

    def test_multiple_synergies_trigger_once_and_are_order_invariant(self):
        decisions = (
            Decision("M1", "Nura"), Decision("M2"), Decision("M10", "Nura"),
            Decision("M12"), Decision("M4", "Esil"),
        )
        expected = simulate_scenario(decisions)
        self.assertTrue(expected.valid)
        self.assertEqual(len(expected.triggered_synergies), 2)
        self.assertEqual(expected.indicators_after["Nura"]["T1"], 64.5)
        self.assertEqual(expected.indicators_after["Nura"]["B1"], 67.5)
        for ordering in permutations(decisions):
            self.assertEqual(simulate_scenario(ordering), expected)

    def test_repeated_simulation_returns_identical_results(self):
        self.assertEqual(simulate_scenario(REFERENCE), simulate_scenario(REFERENCE))

    def test_input_and_output_snapshots_are_independent(self):
        decisions = list(REFERENCE)
        before_decisions = list(decisions)
        result = simulate_scenario(decisions)
        self.assertEqual(decisions, before_decisions)
        result.indicators_after["Nura"]["S1"] = 0
        self.assertEqual(result.indicators_before["Nura"]["S1"], 38)
        result.indicators_before["Nura"]["S1"] = 100
        self.assertEqual(data.DISTRICTS["Nura"].baseline_indicators["S1"], 38)
        next_result = simulate_scenario(REFERENCE)
        self.assertEqual(next_result.indicators_after["Nura"]["S1"], 48)
        self.assertEqual(next_result.indicators_before["Nura"]["S1"], 38)

    def test_valid_scenario_calls_existing_validator_once(self):
        with patch("engine.simulator.validate_scenario", wraps=validate_scenario) as validator:
            result = simulate_scenario(REFERENCE)
        validator.assert_called_once_with(REFERENCE)
        self.assertTrue(result.valid)

    def test_invalid_scenarios_never_enter_effects_or_scoring(self):
        cases = {
            "empty": (),
            "four": REFERENCE[:-1],
            "budget": (
                Decision("M3", "Nura"), Decision("M7", "Nura"), Decision("M8", "Nura"),
                Decision("M5", "Saryarka"), Decision("M10", "Esil"),
            ),
            "duplicate": (
                Decision("M1", "Nura"), Decision("M1", "Esil"), Decision("M4", "Almaty"),
                Decision("M10", "Nura"), Decision("M12"),
            ),
            "incompatible": (
                Decision("M1", "Nura"), Decision("M3", "Esil"), Decision("M4", "Almaty"),
                Decision("M10", "Nura"), Decision("M12"),
            ),
            "unknown": (Decision("M99"),) + REFERENCE[1:],  # type: ignore[arg-type]
            "missing_district": (Decision("M7"),) + REFERENCE[1:],
        }
        guarded = (
            "baseline_indicators", "_apply_effects", "_apply_synergies", "clip_indicators",
            "scoring.calculate_district_scores", "scoring.calculate_d_avg",
            "scoring.minimum_district_score", "scoring.weakest_district",
            "scoring.count_critical_indicators", "scoring.calculate_final_score",
        )
        for name, decisions in cases.items():
            with self.subTest(case=name), ExitStack() as stack:
                mocks = [stack.enter_context(patch("engine.simulator." + path)) for path in guarded]
                validation = validate_scenario(decisions)
                validator = stack.enter_context(patch(
                    "engine.simulator.validate_scenario", return_value=validation,
                ))
                result = simulate_scenario(decisions)
                validator.assert_called_once_with(decisions)
                self.assertFalse(result.valid)
                self.assertEqual(result.validation, validation)
                self.assertEqual(result.budget_used, validation.budget_used)
                self.assertEqual(result.budget_remaining, validation.budget_remaining)
                self.assertEqual(result.triggered_synergies, ())
                for field, value in asdict(result).items():
                    if field not in {"valid", "validation", "budget_used", "budget_remaining", "triggered_synergies"}:
                        self.assertIsNone(value, field)
                for mocked in mocks:
                    mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
