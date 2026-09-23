"""Offline AI adapter tests, including the real SDK with an in-memory transport."""

import json
import os
import unittest
from copy import deepcopy
from dataclasses import asdict, replace
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx2
from openai import APIConnectionError, APIResponseValidationError, APIStatusError, OpenAI

from ai.analyzer import analyze_simulation, get_model_name
from ai.models import (
    AIAnalysis, AIRequestError, AIResponseError, ANALYSIS_SCHEMA,
    InvalidSimulationError, MissingAPIKeyError,
)
from ai.payload import build_analysis_payload
from ai.prompts import ANALYSIS_INSTRUCTIONS
from engine.models import Decision
from engine.simulator import simulate_scenario


EXPLANATION = {
    "summary": "Сценарий улучшает рассчитанное качество жизни; Нура остаётся слабейшим районом.",
    "strengths": ["В Нуре улучшились школьная инфраструктура и первичная медицина."],
    "risks": ["Устранение критических значений не означает решения всех городских проблем."],
    "tradeoffs": ["В сценарии не выбраны транспортные инициативы."],
    "recommendations": ["Рассмотреть транспортный сценарий и отдельно проверить его в симуляторе."],
}


def fake_client(text=None, status="completed", output=None):
    response = SimpleNamespace(
        status=status, output=[] if output is None else output,
        output_text=json.dumps(EXPLANATION, ensure_ascii=False) if text is None else text,
    )
    return SimpleNamespace(responses=SimpleNamespace(create=Mock(return_value=response)))


class AIAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("socket.create_connection", side_effect=AssertionError("Network forbidden")))
        self.enterContext(patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")))
        self.enterContext(patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENAI_MODEL": ""}))
        self.result = simulate_scenario((
            Decision("M7", "Nura"), Decision("M8", "Nura"), Decision("M10", "Nura"),
            Decision("M12"), Decision("M5", "Saryarka"),
        ))

    def test_structured_output_is_converted_to_ai_analysis(self):
        analysis = analyze_simulation(self.result, client=fake_client())
        self.assertIsInstance(analysis, AIAnalysis)
        self.assertEqual(asdict(analysis), EXPLANATION)
        for field in ("strengths", "risks", "tradeoffs", "recommendations"):
            self.assertIsInstance(getattr(analysis, field), list)

    def test_fake_receives_authoritative_payload_and_strict_schema(self):
        client = fake_client()
        analyze_simulation(self.result, client)
        client.responses.create.assert_called_once()
        args = client.responses.create.call_args.kwargs
        self.assertEqual(json.loads(args["input"][0]["content"]), build_analysis_payload(self.result))
        self.assertEqual(args["instructions"], ANALYSIS_INSTRUCTIONS)
        self.assertEqual(args["model"], "gpt-5.6-terra")
        self.assertEqual(args["text"]["format"]["type"], "json_schema")
        self.assertTrue(args["text"]["format"]["strict"])
        self.assertEqual(args["text"]["format"]["schema"], ANALYSIS_SCHEMA)
        self.assertFalse(args["text"]["format"]["schema"]["additionalProperties"])
        self.assertFalse(args["store"])

    def test_output_schema_contains_only_explanation_fields(self):
        self.assertEqual(set(ANALYSIS_SCHEMA["properties"]), set(EXPLANATION))
        self.assertEqual(set(ANALYSIS_SCHEMA["required"]), set(EXPLANATION))

    def test_analysis_does_not_mutate_result(self):
        before = deepcopy(asdict(self.result))
        analyze_simulation(self.result, fake_client())
        self.assertEqual(asdict(self.result), before)

    def test_invalid_result_never_creates_client_or_sends_request(self):
        client = fake_client()
        with patch("ai.analyzer.OpenAI") as factory:
            with self.assertRaises(InvalidSimulationError):
                analyze_simulation(simulate_scenario([]), client)
            with self.assertRaises(InvalidSimulationError):
                analyze_simulation(simulate_scenario([]))
        factory.assert_not_called()
        client.responses.create.assert_not_called()

    def test_incomplete_result_never_sends_request(self):
        client = fake_client()
        with self.assertRaises(InvalidSimulationError):
            analyze_simulation(replace(self.result, score_after=None), client)
        client.responses.create.assert_not_called()

    def test_nonfinite_result_never_sends_request(self):
        client = fake_client()
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(InvalidSimulationError):
                analyze_simulation(replace(self.result, score_after=value), client)
        client.responses.create.assert_not_called()

    def test_missing_or_blank_key_is_controlled(self):
        for value in (None, "", "   "):
            with self.subTest(value=value), patch("ai.analyzer.OpenAI") as factory:
                if value is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = value
                with self.assertRaises(MissingAPIKeyError) as caught:
                    analyze_simulation(self.result)
                self.assertEqual(caught.exception.code, "API_KEY_MISSING")
                self.assertIn("OPENAI_API_KEY", str(caught.exception))
                factory.assert_not_called()

    def test_injected_client_does_not_require_environment_key(self):
        os.environ.pop("OPENAI_API_KEY", None)
        with patch("ai.analyzer.OpenAI") as factory:
            analyze_simulation(self.result, fake_client())
        factory.assert_not_called()

    def test_production_client_reads_key_from_environment_and_is_closed(self):
        client = fake_client()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "unit-test-placeholder"}):
            with patch("ai.analyzer.OpenAI") as factory:
                factory.return_value.__enter__.return_value = client
                analyze_simulation(self.result)
                factory.assert_called_once_with(api_key="unit-test-placeholder", timeout=30.0, max_retries=0)
                factory.return_value.__exit__.assert_called_once()

    def test_injected_client_is_not_closed(self):
        client = fake_client()
        client.close = Mock()
        analyze_simulation(self.result, client)
        client.close.assert_not_called()

    def test_model_can_be_overridden(self):
        with patch.dict(os.environ, {"OPENAI_MODEL": " another-model "}):
            client = fake_client()
            analyze_simulation(self.result, client)
            self.assertEqual(client.responses.create.call_args.kwargs["model"], "another-model")

    def test_default_model_for_unset_and_blank_configuration(self):
        for value in (None, "", "  "):
            if value is None:
                os.environ.pop("OPENAI_MODEL", None)
            else:
                os.environ["OPENAI_MODEL"] = value
            self.assertEqual(get_model_name(), "gpt-5.6-terra")

    def test_api_error_is_sanitized_and_retains_status_code(self):
        client = fake_client()
        request = httpx2.Request("POST", "https://example.invalid/v1/responses")
        response = httpx2.Response(429, request=request)
        client.responses.create.side_effect = APIStatusError(
            "unit-test-secret must not leak", response=response, body={"secret": "unit-test-secret"},
        )
        with self.assertRaises(AIRequestError) as caught:
            analyze_simulation(self.result, client)
        self.assertEqual(caught.exception.code, "OPENAI_REQUEST_FAILED")
        self.assertEqual(caught.exception.status_code, 429)
        self.assertNotIn("unit-test-secret", str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)

    def test_connection_failure_is_controlled(self):
        client = fake_client()
        client.responses.create.side_effect = APIConnectionError(
            request=httpx2.Request("POST", "https://example.invalid/v1/responses"),
        )
        with self.assertRaises(AIRequestError):
            analyze_simulation(self.result, client)

    def test_sdk_response_validation_failure_is_distinct_from_request_error(self):
        client = fake_client()
        response = httpx2.Response(200, request=httpx2.Request("POST", "https://example.invalid"))
        client.responses.create.side_effect = APIResponseValidationError(response=response, body={})
        with self.assertRaises(AIResponseError):
            analyze_simulation(self.result, client)

    def test_unexpected_programming_error_is_not_hidden(self):
        client = fake_client()
        client.responses.create.side_effect = RuntimeError("unexpected programming error")
        with self.assertRaisesRegex(RuntimeError, "unexpected programming error"):
            analyze_simulation(self.result, client)

    def test_malformed_json_is_rejected(self):
        for text in ("not json", "[]", "null", "{}", "{truncated"):
            with self.subTest(text=text), self.assertRaises(AIResponseError):
                analyze_simulation(self.result, fake_client(text=text))

    def test_wrong_field_types_and_extra_numeric_fields_are_rejected(self):
        malformed = [dict(EXPLANATION, score=60.2), dict(EXPLANATION, summary=42)]
        for field in ("strengths", "risks", "tradeoffs", "recommendations"):
            malformed.extend([dict(EXPLANATION, **{field: "text"}), dict(EXPLANATION, **{field: [1]})])
        for value in malformed:
            with self.subTest(value=value), self.assertRaises(AIResponseError):
                analyze_simulation(self.result, fake_client(text=json.dumps(value)))

    def test_empty_and_unexpected_responses_are_rejected(self):
        for response in (None, SimpleNamespace(status="completed"),
                         SimpleNamespace(status="completed", output_text=123),
                         SimpleNamespace(status="completed", output_text=" ")):
            client = fake_client()
            client.responses.create.return_value = response
            with self.subTest(response=response), self.assertRaises(AIResponseError):
                analyze_simulation(self.result, client)

    def test_incomplete_or_cancelled_response_is_not_presented_as_analysis(self):
        for status in ("incomplete", "cancelled", "queued", "in_progress"):
            with self.subTest(status=status), self.assertRaises(AIResponseError):
                analyze_simulation(self.result, fake_client(status=status))

    def test_malformed_output_envelope_is_controlled(self):
        for output in (123, {"message": "wrong shape"}, [SimpleNamespace(content=123)]):
            with self.subTest(output=output), self.assertRaises(AIResponseError):
                analyze_simulation(self.result, fake_client(output=output))

    def test_failed_response_is_request_error(self):
        with self.assertRaises(AIRequestError):
            analyze_simulation(self.result, fake_client(status="failed"))

    def test_refusal_is_not_presented_as_analysis(self):
        refusal = SimpleNamespace(type="message", content=[SimpleNamespace(type="refusal")])
        with self.assertRaises(AIResponseError):
            analyze_simulation(self.result, fake_client(output=[refusal]))

    def test_actual_sdk_uses_responses_json_schema_without_network(self):
        requests = []

        def handler(request):
            requests.append(json.loads(request.content))
            self.assertEqual(request.url.path, "/v1/responses")
            return httpx2.Response(200, json={
                "id": "resp_test", "object": "response", "created_at": 0,
                "status": "completed", "model": "gpt-5.6-terra",
                "error": None, "incomplete_details": None,
                "output": [{
                    "id": "msg_test", "type": "message", "status": "completed", "role": "assistant",
                    "content": [{"type": "output_text", "text": json.dumps(EXPLANATION), "annotations": []}],
                }],
            })

        transport = httpx2.MockTransport(handler)
        with OpenAI(
            api_key="unit-test-placeholder", base_url="https://example.invalid/v1", max_retries=0,
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            analysis = analyze_simulation(self.result, client)
        self.assertEqual(asdict(analysis), EXPLANATION)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["text"]["format"]["schema"], ANALYSIS_SCHEMA)
        self.assertEqual(json.loads(requests[0]["input"][0]["content"]), build_analysis_payload(self.result))


if __name__ == "__main__":
    unittest.main()
