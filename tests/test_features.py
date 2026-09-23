import unittest

from features.comparison import compare_scenarios, summarize_scenario
from features.events import Event, EventResponse, SimulationResult, apply_event
from features.optimization import CandidateScenario, find_best_scenarios


class FeatureTests(unittest.TestCase):
    def test_event_returns_updated_copy_and_preserves_original(self):
        original = SimulationResult({"temperature": 2.0}, budget_used=10)
        event = Event(
            "Heavy snowfall",
            "Transport disruption",
            {"temperature": -8},
            (EventResponse("Emergency response", {"temperature": 4}, 8),),
        )

        applied = apply_event(original, event, event.responses[0])

        self.assertEqual(applied.result.metrics["temperature"], -2)
        self.assertEqual(applied.result.budget_used, 18)
        self.assertEqual(original.metrics["temperature"], 2)

    def test_event_rejects_unknown_response(self):
        event = Event("Road closure", "Major road closed")
        response = EventResponse("Unknown")
        with self.assertRaises(ValueError):
            apply_event(SimulationResult({}), event, response)

    def test_comparison_produces_table_rows(self):
        scenario = summarize_scenario("A", SimulationResult({"Nura": -1, "East": 2}), 56.54)
        self.assertEqual(
            compare_scenarios([scenario]),
            [{"name": "A", "budget": 0.0, "score": 56.54, "critical": 1, "critical_metrics": ("Nura",), "weakest": "Nura"}],
        )

    def test_optimizer_returns_valid_deterministic_top_n(self):
        def simulator(candidate: CandidateScenario) -> SimulationResult:
            return SimulationResult({"score": len(candidate.decisions) + candidate.decisions.count("strong")})

        results = find_best_scenarios(
            [["weak", "strong"], ["weak", "strong"]],
            validator=lambda candidate: candidate.decisions != ("weak", "weak"),
            simulator=simulator,
            scorer=lambda result: result.metrics["score"],
            top_n=2,
        )

        self.assertEqual(
            [item.candidate.decisions for item in results.scenarios],
            [("strong", "strong"), ("strong", "weak")],
        )

    def test_optimizer_enforces_limit_and_reports_empty_search(self):
        calls = 0

        def simulator(candidate: CandidateScenario) -> SimulationResult:
            nonlocal calls
            calls += 1
            return SimulationResult({"score": 1})

        result = find_best_scenarios(
            [["a", "b"], ["a", "b"]],
            validator=lambda candidate: False,
            simulator=simulator,
            scorer=lambda simulation: simulation.metrics["score"],
            max_checked=2,
        )

        self.assertEqual(result.checked_count, 2)
        self.assertEqual(result.valid_count, 0)
        self.assertTrue(result.truncated)
        self.assertEqual(calls, 0)
        self.assertEqual(result.scenarios, ())

    def test_optimizer_ties_prefer_lower_budget(self):
        def simulator(candidate: CandidateScenario) -> SimulationResult:
            return SimulationResult({"score": 10}, budget_used=20 if candidate.decisions[0] == "expensive" else 5)

        result = find_best_scenarios(
            [["expensive", "cheap"]],
            validator=lambda candidate: True,
            simulator=simulator,
            scorer=lambda simulation: simulation.metrics["score"],
        )

        self.assertEqual(result.scenarios[0].candidate.decisions, ("cheap",))


if __name__ == "__main__":
    unittest.main()