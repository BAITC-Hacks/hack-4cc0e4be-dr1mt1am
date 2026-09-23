"""Payload facts come from a real simulator result, never a parallel calculation."""

import json
import unittest
from copy import deepcopy
from dataclasses import asdict, replace
from unittest.mock import patch

from ai.models import InvalidSimulationError
from ai.payload import build_analysis_payload
from engine.models import Decision
from engine.simulator import simulate_scenario


class AIPayloadTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("socket.create_connection", side_effect=AssertionError("Network forbidden")))
        self.enterContext(patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")))
        self.decisions = (
            Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M10", "Nura"),
            Decision("M12"), Decision("M5", "Saryarka"),
        )
        self.result = simulate_scenario(self.decisions)

    def test_reference_payload_scores_and_budget(self):
        payload = build_analysis_payload(self.result)
        self.assertAlmostEqual(payload["score_before"], 52.55768, places=10)
        self.assertAlmostEqual(payload["score_after"], 56.54307, places=10)
        self.assertAlmostEqual(payload["score_delta"], 3.98539, places=10)
        self.assertEqual(payload["budget_used"], 95)
        self.assertEqual(payload["budget_remaining"], 5)
        self.assertEqual((payload["n_crit_before"], payload["n_crit_after"]), (2, 0))

    def test_reference_selected_initiatives_and_targets(self):
        selected = build_analysis_payload(self.result)["selected_initiatives"]
        self.assertEqual({item["id"]: item["target_district"] for item in selected}, {
            "M7": "Nura", "M8": "Nura", "M10": "Nura", "M12": None, "M5": "Saryarka",
        })
        self.assertEqual(len(selected), 5)
        by_id = {item["id"]: item for item in selected}
        self.assertEqual(by_id["M7"]["cost"], 24)
        self.assertEqual(by_id["M7"]["direction"], "Social")
        self.assertEqual(by_id["M12"]["type"], "City")
        self.assertEqual(by_id["M12"]["name"], "Unified digital resident request platform")

    def test_reference_triggered_synergy(self):
        self.assertEqual(build_analysis_payload(self.result)["triggered_synergies"], [{
            "initiative_ids": ["M10", "M12"], "target_district": "Nura",
            "bonuses": [{"indicator": "B1", "delta": 2}],
        }])

    def test_all_required_facts_are_copied_exactly(self):
        payload = build_analysis_payload(self.result)
        fields = (
            "score_before", "score_after", "score_delta", "budget_used", "budget_remaining",
            "district_scores_before", "district_scores_after", "district_score_changes",
            "indicators_before", "indicators_after", "indicator_changes",
            "d_avg_before", "d_avg_after", "weakest_district_before", "weakest_district_after",
            "min_district_score_before", "min_district_score_after", "n_crit_before", "n_crit_after",
        )
        for name in fields:
            self.assertEqual(payload[name], getattr(self.result, name), name)

    def test_payload_does_not_recompute_scores_or_changes(self):
        supplied = replace(
            self.result, score_before=11.123456789, score_after=22.87654321,
            score_delta=7.23456789, district_score_changes={"Nura": 99.125},
            indicator_changes={"Nura": {"S1": 2.3456789}},
        )
        with patch("engine.scoring.calculate_final_score", side_effect=AssertionError("No scoring in AI")):
            payload = build_analysis_payload(supplied)
        self.assertEqual(payload["score_before"], 11.123456789)
        self.assertEqual(payload["score_after"], 22.87654321)
        self.assertEqual(payload["score_delta"], 7.23456789)
        self.assertEqual(payload["district_score_changes"], {"Nura": 99.125})
        self.assertEqual(payload["indicator_changes"], {"Nura": {"S1": 2.3456789}})

    def test_new_explanation_facts_are_calculated_by_engine(self):
        self.assertAlmostEqual(self.result.district_score_changes["Nura"], 3.7825, places=10)
        self.assertAlmostEqual(self.result.district_score_changes["Saryarka"], 1.65, places=10)
        self.assertEqual(self.result.indicator_changes["Nura"]["S1"], 10)
        self.assertEqual(self.result.indicator_changes["Nura"]["B1"], 12.5)
        self.assertEqual(self.result.indicator_changes["Esil"]["C2"], 4.375)
        self.assertEqual({item.decision for item in self.result.selected_initiatives}, set(self.decisions))

    def test_indicator_names_and_directions_are_available(self):
        metadata = build_analysis_payload(self.result)["indicator_metadata"]
        self.assertEqual(len(metadata), 10)
        self.assertEqual(metadata["S1"]["direction"], "Social")
        self.assertEqual(metadata["T2"]["name"], "Public transport accessibility")
        self.assertTrue(all(item["higher_is_better"] for item in metadata.values()))

    def test_payload_is_json_serializable_without_rounding(self):
        payload = build_analysis_payload(self.result)
        self.assertEqual(json.loads(json.dumps(payload, allow_nan=False)), payload)

    def test_payload_build_does_not_mutate_simulation(self):
        before = deepcopy(asdict(self.result))
        build_analysis_payload(self.result)
        self.assertEqual(asdict(self.result), before)

    def test_payload_mutation_cannot_change_simulation(self):
        before = deepcopy(asdict(self.result))
        payload = build_analysis_payload(self.result)
        payload["indicators_after"]["Nura"]["S1"] = -100
        payload["district_scores_after"]["Nura"] = -100
        payload["indicator_changes"]["Nura"]["S1"] = -100
        payload["selected_initiatives"][0]["cost"] = -100
        payload["triggered_synergies"][0]["bonuses"][0]["delta"] = -100
        self.assertEqual(asdict(self.result), before)

    def test_repeated_payload_build_is_identical(self):
        self.assertEqual(build_analysis_payload(self.result), build_analysis_payload(self.result))

    def test_invalid_result_is_rejected(self):
        with self.assertRaises(InvalidSimulationError):
            build_analysis_payload(simulate_scenario([]))

    def test_inconsistent_validation_flag_is_rejected(self):
        result = replace(self.result, validation=replace(self.result.validation, valid=False))
        with self.assertRaises(InvalidSimulationError):
            build_analysis_payload(result)

    def test_incomplete_valid_result_is_rejected_instead_of_inventing_values(self):
        for missing in ("score_after", "indicators_after", "selected_initiatives", "indicator_changes"):
            with self.subTest(field=missing), self.assertRaises(InvalidSimulationError):
                build_analysis_payload(replace(self.result, **{missing: None}))


if __name__ == "__main__":
    unittest.main()
