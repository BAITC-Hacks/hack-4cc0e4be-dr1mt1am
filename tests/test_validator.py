"""Public-boundary tests for scenario validation, without running simulation."""

import unittest
from dataclasses import asdict, replace
from itertools import permutations

from engine import constants, data
from engine.models import Decision, ValidationResult
from engine.validator import validate_scenario


REFERENCE = (
    Decision("M7", "Nura"), Decision("M8", "Nura"),
    Decision("M10", "Nura"), Decision("M12"), Decision("M5", "Saryarka"),
)
CHEAP = (
    Decision("M1", "Nura"), Decision("M4", "Esil"),
    Decision("M9", "Almaty"), Decision("M10", "Nura"), Decision("M12"),
)


class ValidatorTests(unittest.TestCase):
    def assert_errors(self, decisions, *codes):
        result = validate_scenario(decisions)
        self.assertFalse(result.valid)
        self.assertCountEqual([issue.code for issue in result.errors], codes)
        for issue in result.errors:
            self.assertRegex(issue.message, "[А-Яа-яЁё]")
        return result

    def assert_valid(self, decisions, used, remaining):
        result = validate_scenario(decisions)
        self.assertEqual(result, ValidationResult(True, [], used, remaining))
        return result

    def test_reference_scenario_without_transport_is_valid(self):
        self.assert_valid(REFERENCE, 95, 5)

    def test_budget_exactly_100_is_valid(self):
        self.assert_valid((
            Decision("M3", "Nura"), Decision("M7", "Nura"), Decision("M6"),
            Decision("M10", "Esil"), Decision("M12"),
        ), 100, 0)

    def test_two_initiatives_from_one_direction_are_valid(self):
        self.assert_valid((
            Decision("M1", "Nura"), Decision("M2"), Decision("M4", "Esil"),
            Decision("M10", "Nura"), Decision("M12"),
        ), 81, 19)

    def test_m4_m7_in_different_districts_are_valid(self):
        self.assert_valid((
            Decision("M4", "Esil"), Decision("M7", "Nura"), Decision("M1", "Nura"),
            Decision("M10", "Esil"), Decision("M12"),
        ), 83, 17)

    def test_m5_m13_in_different_districts_are_valid(self):
        self.assert_valid((
            Decision("M5", "Saryarka"), Decision("M13", "Almaty"),
            Decision("M9", "Nura"), Decision("M10", "Nura"), Decision("M11", "Esil"),
        ), 85, 15)

    def test_synergy_pair_is_not_a_restriction(self):
        self.assert_valid((
            Decision("M5", "Saryarka"), Decision("M6"), Decision("M9", "Nura"),
            Decision("M10", "Nura"), Decision("M12"),
        ), 81, 19)

    def test_zero_decisions(self):
        result = self.assert_errors([], "INVALID_DECISION_COUNT")
        self.assertEqual((result.budget_used, result.budget_remaining), (0, 100))

    def test_four_decisions(self):
        self.assert_errors(CHEAP[:-1], "INVALID_DECISION_COUNT")

    def test_six_decisions(self):
        self.assert_errors(CHEAP + (Decision("M11", "Esil"),), "INVALID_DECISION_COUNT")

    def test_unknown_initiative_returns_unknown_budget_without_target_errors(self):
        # Literal annotations do not enforce runtime membership; keep the model unchanged.
        decisions = (Decision("M99"),) + REFERENCE[1:]  # type: ignore[arg-type]
        result = self.assert_errors(decisions, "UNKNOWN_INITIATIVE")
        self.assertIsNone(result.budget_used)
        self.assertIsNone(result.budget_remaining)

    def test_unknown_initiative_does_not_report_partial_over_budget(self):
        decisions = (
            Decision("M3", "Nura"), Decision("M7", "Nura"), Decision("M13", "Almaty"),
            Decision("M5", "Saryarka"), Decision("M99"),  # type: ignore[arg-type]
        )
        result = self.assert_errors(decisions, "UNKNOWN_INITIATIVE")
        self.assertIsNone(result.budget_used)
        self.assertIsNone(result.budget_remaining)

    def test_duplicate_initiative_is_charged_for_each_occurrence(self):
        result = self.assert_errors((
            Decision("M1", "Nura"), Decision("M1", "Nura"), Decision("M4", "Esil"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DUPLICATE_INITIATIVE")
        self.assertEqual((result.budget_used, result.budget_remaining), (77, 23))

    def test_duplicate_initiative_in_different_districts(self):
        self.assert_errors((
            Decision("M1", "Nura"), Decision("M1", "Esil"), Decision("M4", "Almaty"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DUPLICATE_INITIATIVE")

    def test_duplicate_unknown_id_reports_each_issue_only_once(self):
        result = self.assert_errors((
            Decision("M99"), Decision("M99"),  # type: ignore[arg-type]
            Decision("M4", "Esil"), Decision("M10", "Nura"), Decision("M12"),
        ), "DUPLICATE_INITIATIVE", "UNKNOWN_INITIATIVE")
        self.assertIsNone(result.budget_used)
        self.assertIsNone(result.budget_remaining)

    def test_budget_exceeded_returns_negative_remaining_budget(self):
        result = self.assert_errors((
            Decision("M3", "Nura"), Decision("M7", "Nura"), Decision("M8", "Nura"),
            Decision("M5", "Saryarka"), Decision("M10", "Esil"),
        ), "BUDGET_EXCEEDED")
        self.assertEqual((result.budget_used, result.budget_remaining), (111, -11))

    def test_duplicates_can_also_exceed_budget(self):
        result = self.assert_errors((
            Decision("M3", "Nura"), Decision("M3", "Esil"), Decision("M7", "Nura"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DUPLICATE_INITIATIVE", "BUDGET_EXCEEDED")
        self.assertEqual((result.budget_used, result.budget_remaining), (110, -10))

    def test_three_initiatives_from_one_direction(self):
        self.assert_errors((
            Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M9", "Esil"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DIRECTION_LIMIT_EXCEEDED")

    def test_missing_district(self):
        self.assert_errors((replace(REFERENCE[0], district=None),) + REFERENCE[1:], "DISTRICT_REQUIRED")

    def test_unknown_district(self):
        self.assert_errors((
            replace(REFERENCE[0], district="Unknown"),  # type: ignore[arg-type]
        ) + REFERENCE[1:], "UNKNOWN_DISTRICT")

    def test_empty_district_name_is_unknown_not_missing(self):
        self.assert_errors((
            replace(REFERENCE[0], district=""),  # type: ignore[arg-type]
        ) + REFERENCE[1:], "UNKNOWN_DISTRICT")

    def test_city_initiative_must_have_none_as_district(self):
        for district in ("Nura", "город", "city", "Unknown", ""):
            with self.subTest(district=district):
                decisions = list(REFERENCE)
                decisions[3] = Decision("M12", district)  # type: ignore[arg-type]
                self.assert_errors(decisions, "DISTRICT_NOT_ALLOWED")

    def test_m1_m3_same_district(self):
        result = self.assert_errors((
            Decision("M1", "Nura"), Decision("M3", "Nura"), Decision("M4", "Almaty"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "INCOMPATIBLE_INITIATIVES")
        self.assertIn("M1", result.errors[0].message)
        self.assertIn("M3", result.errors[0].message)

    def test_m1_m3_different_districts(self):
        self.assert_errors((
            Decision("M1", "Nura"), Decision("M3", "Esil"), Decision("M4", "Almaty"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "INCOMPATIBLE_INITIATIVES")

    def test_m4_m7_same_district(self):
        result = self.assert_errors((
            Decision("M4", "Nura"), Decision("M7", "Nura"), Decision("M1", "Nura"),
            Decision("M10", "Esil"), Decision("M12"),
        ), "INCOMPATIBLE_INITIATIVES")
        for value in ("M4", "M7", "Nura"):
            self.assertIn(value, result.errors[0].message)

    def test_m5_m13_same_district(self):
        result = self.assert_errors((
            Decision("M5", "Saryarka"), Decision("M13", "Saryarka"),
            Decision("M9", "Nura"), Decision("M10", "Nura"), Decision("M11", "Esil"),
        ), "INCOMPATIBLE_INITIATIVES")
        for value in ("M5", "M13", "Saryarka"):
            self.assertIn(value, result.errors[0].message)

    def test_invalid_districts_do_not_create_same_district_conflicts(self):
        for district, code in ((None, "DISTRICT_REQUIRED"), ("Unknown", "UNKNOWN_DISTRICT")):
            with self.subTest(district=district):
                self.assert_errors((
                    Decision("M4", district), Decision("M7", district),  # type: ignore[arg-type]
                    Decision("M1", "Nura"), Decision("M10", "Esil"), Decision("M12"),
                ), code, code)

    def test_scenario_conflict_is_independent_of_missing_districts(self):
        self.assert_errors((
            Decision("M1"), Decision("M3"), Decision("M4", "Almaty"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DISTRICT_REQUIRED", "DISTRICT_REQUIRED", "INCOMPATIBLE_INITIATIVES")

    def test_conflicts_consider_all_targets_of_repeated_initiative(self):
        decisions = (
            Decision("M4", "Esil"), Decision("M4", "Nura"), Decision("M7", "Nura"),
            Decision("M10", "Esil"), Decision("M12"),
        )
        expected = self.assert_errors(decisions, "DUPLICATE_INITIATIVE", "INCOMPATIBLE_INITIATIVES")
        for ordering in permutations(decisions):
            self.assertEqual(validate_scenario(ordering), expected)

    def test_repeated_target_errors_are_deduplicated(self):
        self.assert_errors((
            Decision("M1"), Decision("M1"), Decision("M4", "Esil"),
            Decision("M10", "Nura"), Decision("M12"),
        ), "DUPLICATE_INITIATIVE", "DISTRICT_REQUIRED")

    def test_multiple_independent_errors_are_collected(self):
        self.assert_errors((
            Decision("M1"), Decision("M1", "Nura"), Decision("M3", "Nura"),
            Decision("M12", "Esil"), Decision("M99"), Decision("M4"),  # type: ignore[arg-type]
        ), "INVALID_DECISION_COUNT", "DUPLICATE_INITIATIVE", "DISTRICT_REQUIRED",
            "DISTRICT_REQUIRED", "DISTRICT_NOT_ALLOWED", "UNKNOWN_INITIATIVE",
            "DIRECTION_LIMIT_EXCEEDED", "INCOMPATIBLE_INITIATIVES")

    def test_reference_all_120_permutations_return_identical_result(self):
        expected = ValidationResult(True, [], 95, 5)
        count = 0
        for ordering in permutations(REFERENCE):
            self.assertEqual(validate_scenario(ordering), expected)
            count += 1
        self.assertEqual(count, 120)

    def test_invalid_permutations_preserve_complete_error_order(self):
        decisions = (
            Decision("M1", "Nura"), Decision("M1", "Esil"), Decision("M3", "Nura"),
            Decision("M12", "Nura"), Decision("M99"),  # type: ignore[arg-type]
        )
        expected = self.assert_errors(
            decisions, "DUPLICATE_INITIATIVE", "DIRECTION_LIMIT_EXCEEDED",
            "INCOMPATIBLE_INITIATIVES", "DISTRICT_NOT_ALLOWED", "UNKNOWN_INITIATIVE",
        )
        for ordering in permutations(decisions):
            self.assertEqual(validate_scenario(ordering), expected)

    def test_repeated_calls_return_equal_results(self):
        for decisions in (REFERENCE, (), CHEAP + (Decision("M11", "Esil"),)):
            self.assertEqual(validate_scenario(decisions), validate_scenario(decisions))

    def test_input_list_and_decisions_remain_unchanged(self):
        decisions = list(reversed(REFERENCE))
        before = [asdict(decision) for decision in decisions]
        original_objects = list(decisions)
        validate_scenario(decisions)
        self.assertEqual([asdict(decision) for decision in decisions], before)
        self.assertTrue(all(first is second for first, second in zip(decisions, original_objects)))

    def test_static_data_remains_unchanged(self):
        def snapshot():
            return repr((
                data.DISTRICTS, data.INITIATIVES, data.INDICATORS, data.INDICATOR_WEIGHTS,
                data.POPULATION_SHARES, data.DIRECTION_WEIGHTS, data.SYNERGIES,
                data.INCOMPATIBILITIES,
                {name: value for name, value in vars(constants).items() if name.isupper()},
            ))

        before = snapshot()
        validate_scenario(REFERENCE)
        validate_scenario(CHEAP + (Decision("M1", "Nura"),))
        validate_scenario((Decision("M99"),))  # type: ignore[arg-type]
        self.assertEqual(snapshot(), before)

    def test_result_structure_has_no_score(self):
        self.assertEqual(asdict(validate_scenario(REFERENCE)), {
            "valid": True, "errors": [], "budget_used": 95, "budget_remaining": 5,
        })
        invalid = asdict(validate_scenario([]))
        self.assertEqual(set(invalid), {"valid", "errors", "budget_used", "budget_remaining"})
        self.assertEqual(set(invalid["errors"][0]), {"code", "message"})


if __name__ == "__main__":
    unittest.main()
