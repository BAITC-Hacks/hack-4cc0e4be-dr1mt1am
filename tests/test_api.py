"""FastAPI contract tests: real engine, in-process HTTP, no OpenAI network."""

import os
import unittest
from copy import deepcopy
from dataclasses import asdict, replace
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai.models import AIAnalysis, AIRequestError, AIResponseError
from api.app import create_app
from api.serializers import json_snapshot, simulation_response
from engine.constants import BUDGET, HORIZON_QUARTERS
from engine.data import DISTRICTS, INITIATIVES, INDICATORS, SYNERGIES, INCOMPATIBILITIES
from engine.models import Decision
from engine.simulator import simulate_scenario


REFERENCE = [Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M10", "Nura"), Decision("M12"), Decision("M5", "Saryarka")]


class APITests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {"OPENAI_API_KEY": "", "FRONTEND_ORIGIN": "http://localhost:5173"}))
        self.provider = self.enterContext(patch("ai.analyzer.OpenAI", side_effect=AssertionError("OpenAI network forbidden")))
        self.client = self.enterContext(TestClient(create_app()))
        self.request = {"decisions": [asdict(item) for item in REFERENCE]}

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_catalog_uses_authoritative_data_and_calculated_baseline(self):
        response = self.client.get("/api/catalog")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["budget"], BUDGET)
        self.assertEqual(data["horizon"], HORIZON_QUARTERS)
        self.assertAlmostEqual(data["baseline_score"], 52.55768, places=10)
        self.assertEqual(data["baseline_n_crit"], 2)
        self.assertEqual(data["weakest_district"], "Nura")
        self.assertEqual(len(data["districts"]), len(DISTRICTS))
        self.assertEqual(len(data["initiatives"]), len(INITIATIVES))
        self.assertEqual(data["indicator_metadata"], json_snapshot(INDICATORS))
        self.assertEqual(data["synergies"], json_snapshot(SYNERGIES))
        self.assertEqual(data["incompatibilities"], json_snapshot(INCOMPATIBILITIES))
        for item in data["initiatives"]:
            source = INITIATIVES[item["id"]]
            self.assertEqual((item["cost"], item["lag"], item["direction"], item["type"]), (source.cost, source.lag, source.direction.value, source.type.value))
            self.assertEqual(item["effects"], [[effect.indicator, effect.delta] for effect in source.effects])
        for district in data["districts"]:
            self.assertEqual(district["indicators"], dict(DISTRICTS[district["id"]].baseline_indicators))

    def test_reference_simulation_full_precision(self):
        response = self.client.post("/api/simulate", json=self.request)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        self.assertAlmostEqual(data["score_after"], 56.54307, places=10)
        self.assertAlmostEqual(data["score_delta"], 3.98539, places=10)
        self.assertEqual((data["budget_used"], data["budget_remaining"]), (95, 5))
        self.assertEqual((data["n_crit_before"], data["n_crit_after"]), (2, 0))
        self.assertEqual(data["weakest_district_after"], "Nura")
        self.assertEqual(data["triggered_synergies"][0]["district"], "Nura")
        self.assertEqual(data["triggered_synergies"][0]["synergy"]["first_initiative_id"], "M10")
        self.assertEqual(data, simulation_response(simulate_scenario(REFERENCE)))

    def test_simulation_delegates_without_recomputing_result(self):
        supplied = replace(simulate_scenario(REFERENCE), score_after=12.345678901, score_delta=-99.12345)
        with patch("api.app.simulate_scenario", return_value=supplied) as simulate:
            data = self.client.post("/api/simulate", json=self.request).json()
        simulate.assert_called_once_with(tuple(REFERENCE))
        self.assertEqual(data["score_after"], supplied.score_after)
        self.assertEqual(data["score_delta"], supplied.score_delta)

    def test_invalid_scenario_has_validation_and_no_score(self):
        data = self.client.post("/api/simulate", json={"decisions": []}).json()
        self.assertFalse(data["valid"])
        self.assertEqual(data["errors"][0]["code"], "INVALID_DECISION_COUNT")
        self.assertNotIn("score_after", data)

    def test_unknown_initiative_reaches_engine_validator(self):
        request = deepcopy(self.request)
        request["decisions"][0]["initiative_id"] = "M999"
        response = self.client.post("/api/simulate", json=request)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("UNKNOWN_INITIATIVE", [item["code"] for item in data["errors"]])
        self.assertIsNone(data["budget_used"])

    def test_budget_exceeded(self):
        decisions = [Decision("M3", "Nura"), Decision("M5", "Saryarka"), Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M13", "Esil")]
        data = self.client.post("/api/simulate", json={"decisions": [asdict(item) for item in decisions]}).json()
        self.assertFalse(data["valid"])
        self.assertGreater(data["budget_used"], BUDGET)
        self.assertEqual(data["errors"], json_snapshot(simulate_scenario(decisions).validation.errors))

    def test_client_generated_scores_and_wrong_types_are_rejected(self):
        for request in ({**self.request, "score_after": 100}, {"decisions": [{"initiative_id": 7}]}, {"decisions": [{"initiative_id": "M7", "cost": 0}]}):
            with self.subTest(request=request):
                response = self.client.post("/api/analyze", json=request)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["error"]["code"], "INVALID_REQUEST")
        self.provider.assert_not_called()

    def test_ai_invalid_scenario_never_calls_analyzer(self):
        with patch("api.app.analyze_simulation") as analyze:
            data = self.client.post("/api/analyze", json={"decisions": []}).json()
        self.assertFalse(data["valid"])
        analyze.assert_not_called()
        self.provider.assert_not_called()

    def test_ai_success_receives_server_calculated_result(self):
        analysis = AIAnalysis("Краткий итог", ["Сильная сторона"], ["Риск"], ["Компромисс"], ["Проверить альтернативу"])
        with patch("api.app.analyze_simulation", return_value=analysis) as analyze, patch("api.app.simulate_scenario", wraps=simulate_scenario) as simulate:
            response = self.client.post("/api/analyze", json=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), asdict(analysis))
        simulate.assert_called_once_with(tuple(REFERENCE))
        analyze.assert_called_once_with(simulate_scenario(REFERENCE))

    def test_missing_key_is_controlled_and_simulation_still_works(self):
        response = self.client.post("/api/analyze", json=self.request)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "API_KEY_MISSING")
        self.assertTrue(self.client.post("/api/simulate", json=self.request).json()["valid"])
        self.provider.assert_not_called()

    def test_ai_errors_do_not_expose_provider_details(self):
        for error in (AIRequestError("private-provider-secret"), AIResponseError("private-provider-secret")):
            with patch("api.app.analyze_simulation", side_effect=error):
                response = self.client.post("/api/analyze", json=self.request)
            self.assertEqual(response.status_code, 502)
            self.assertNotIn("private-provider-secret", response.text)
            self.assertEqual(response.json()["error"]["code"], error.code)

    def test_cors_allows_only_configured_origin(self):
        headers = {"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"}
        response = self.client.options("/api/simulate", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], headers["Origin"])
        response = self.client.get("/api/catalog", headers={"Origin": "https://untrusted.invalid"})
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_cors_origin_can_be_overridden(self):
        with patch.dict(os.environ, {"FRONTEND_ORIGIN": "http://localhost:5174"}), TestClient(create_app()) as client:
            response = client.get("/api/health", headers={"Origin": "http://localhost:5174"})
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5174")

    def test_serialization_does_not_mutate_or_share_result(self):
        result = simulate_scenario(REFERENCE)
        before = deepcopy(asdict(result))
        serialized = simulation_response(result)
        serialized["indicators_after"]["Nura"]["S1"] = -100
        serialized["triggered_synergies"].clear()
        self.assertEqual(asdict(result), before)


if __name__ == "__main__":
    unittest.main()
