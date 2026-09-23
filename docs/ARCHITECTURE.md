# Architecture

The deterministic engine is authoritative for every numerical result. Business rules and constants live in [PROJECT_SPEC.md](PROJECT_SPEC.md); implementation priorities live in [TASKS.md](TASKS.md).

```text
Decision[]
-> validate_scenario (called inside simulate_scenario)
-> simulate_scenario + scoring
-> SimulationResult
-> analyze_simulation
-> AIAnalysis
-> UI (future integration)
```

| Component / expected location | Responsibility |
| --- | --- |
| User selections / `ui/` | Collect initiative IDs and district targets, display budget and validation feedback, and submit decisions to the validator. |
| Validator / `engine/validator.py` | Enforce budget, exactly five decisions, uniqueness, direction limits, target rules, and incompatibilities. Return actionable validation errors for invalid scenarios; do not pass them to simulation or scoring. |
| Simulation Engine / `engine/simulator.py` | Starting from baseline data, apply normal lag-scaled effects to district or city targets, add fixed synergy bonuses, then clip final indicators. Be deterministic and independent of decision order. |
| Scoring Engine / `engine/scoring.py` | Calculate district scores, population-weighted `D_avg`, `N_crit`, and the final Astana Quality of Life Score from calculated indicators using the specification. Preserve full precision. |
| Structured `SimulationResult` / `engine/models.py` | Carry validation, budget used/remaining, independent before/after indicator snapshots, district scores, population-weighted averages, weakest districts and minimum scores, critical counts, final scores and delta, triggered synergies, selected decisions with their catalog records, and engine-calculated district/indicator changes. Invalid scenarios have no simulation or score values. |
| AI Analyzer / `ai/analyzer.py` | Consume structured calculated output and explain strengths, weaknesses, risks, trade-offs, comparisons, and recommendations. Clearly distinguish facts from analysis and recommendations. |
| Results UI / `ui/` | Display calculated values and explanations, before/after views, and district comparisons. Round only for presentation. |
| Domain models / `engine/models.py` | Frozen typed records for districts, initiatives, effects, decisions, synergies, incompatibilities, indicator metadata, validation issues/results, triggered synergies, and simulation results. These records do not execute validation or simulation rules. |
| Static data / `engine/data.py`, `engine/constants.py` | Hold baseline districts, population shares, indicator weights, initiative catalog, synergies, incompatibilities, and constants exactly as specified. Python modules are authoritative at this stage; `data/` is reserved for possible future file assets. |
| Tests / `tests/` | Cover validation, simulation, scoring, baseline/reference regressions, and order invariance. |

## Boundaries

- No scoring logic in the UI; consume engine output instead of duplicating formulas.
- No official scoring in AI; the analyzer must not change or fabricate simulator values.
- Simulation and scoring must remain usable and testable without UI or LLM access.
- Invalid scenarios receive validation feedback and no Score. Baseline scoring is a separate comparison fixture, not a valid zero-decision user scenario.
- In a synergy pair, the first initiative is the first member listed in the specification, independent of user selection order.
- Use the explicitly confirmed scoring clarification below; preserve the supplied regression targets.

Typed domain models, static data, validation, simulation, scoring, and AI explanation are implemented and tested. `validate_scenario(decisions: Sequence[Decision]) -> ValidationResult` returns Russian error messages with stable codes, plus budget used/remaining (both `None` for unknown initiative IDs). Repeated selections each count toward cost and direction limits. Errors are deduplicated and sorted by code and message, independent of decision order. UI remains unimplemented.

## Simulation API

`simulate_scenario(decisions: Sequence[Decision]) -> SimulationResult` calls the existing validator once. Invalid input returns immediately, before copying baseline or performing any scoring. Valid input creates independent before/after snapshots, applies normal effects in initiative-ID order, applies each selected synergy once, then clips and scores. No rounding occurs in the engine. Equal weakest-district scores are resolved alphabetically by district identifier.

The result dataclass is frozen; its nested snapshot dictionaries are independent copies, not shared static data. Consumers can access all requested before/after values directly. `triggered_synergies` contains `TriggeredSynergy(synergy, district)` records referring to the immutable catalog definitions.

## Confirmed scoring clarification

On 2026-09-23 the user explicitly confirmed:

```text
Score = 0.7 * D_avg + 0.3 * min(D_d) - 1.0 * N_crit
```

The supplied specification's `* 1.0 * N_crit` line was inconsistent with its stated penalty and regression values. The unpenalized baseline is 54.55768; subtracting two critical pairs gives 52.55768. The reference scenario has zero critical pairs and yields 56.54307. The implementation follows this explicit user clarification. PROJECT_SPEC.md itself remains unchanged at the user's request.

## AI explanation API

`SimulationResult` is the numerical source of truth. `AIAnalysis` is explanation only.

`build_analysis_payload(result: SimulationResult) -> dict[str, Any]` copies calculated values without recalculating scores or deltas. At this presentation boundary, floats are rounded to at most two decimal places and remain JSON numbers; budgets and critical counts remain integers. The original `SimulationResult` retains full precision. The payload includes selected initiatives and targets, triggered synergies, engine-calculated district/indicator changes, and descriptive indicator metadata from the existing catalog. It creates independent nested data. Missing simulation fields cause a controlled error instead of invented values. No aggregate direction ranking is defined, so the prompt requires the model to acknowledge that limitation.

`analyze_simulation(result: SimulationResult, client: OpenAI | None = None) -> AIAnalysis` uses OpenAI Responses API with a strict JSON Schema in `text.format`. The output is a frozen dataclass with `summary: str` and `strengths`, `risks`, `tradeoffs`, `recommendations: list[str]`. It has no numeric Score, budget, or indicator fields. Completed JSON is checked for exact keys and types; refusal, incomplete output, and invalid output are errors, never fabricated fallback explanations.

The prompt requests Russian explanations, separates simulator facts from interpretation and recommendations, prohibits new numerical calculations or forecasts, and treats payload strings as data. Structured Outputs constrain shape, not factual correctness; live answer quality still needs evaluation before presentation to users. Recommendations require a new engine run before any numerical outcome can be stated. Scenario comparison is not implemented.

Configuration and dependencies:

- Install the single direct dependency with `.venv\Scripts\python.exe -m pip install -r requirements.txt`. The tested SDK is pinned to `openai==3.19.0`.
- Set `OPENAI_API_KEY` in the process environment. The analyzer never writes or logs it. `.env` is ignored by Git but is not automatically loaded.
- `OPENAI_MODEL` overrides the requested default `gpt-5.6-terra`. Availability and Structured Outputs support for the chosen model must be checked with the deployment account; no live API request was made during implementation.
- A client supplied by the caller controls its credentials and lifecycle. The analyzer creates and closes its own client only when none is supplied, using a 30-second timeout and no automatic retries.

Errors for UI handling (all inherit `AIAnalysisError`):

| Exception | Stable code | Meaning |
| --- | --- | --- |
| `InvalidSimulationError` (also `ValueError`) | `SIMULATION_INVALID` | Invalid, incomplete, or unserializable simulation; no request sent. |
| `MissingAPIKeyError` | `API_KEY_MISSING` | No usable environment key for a client created by the analyzer. |
| `AIRequestError` | `OPENAI_REQUEST_FAILED` | SDK request failure or failed response; optional HTTP `status_code`. |
| `AIResponseError` | `AI_RESPONSE_INVALID` | Refused, incomplete, empty, malformed, or unexpected response. |

Provider response bodies and raw exception messages are not exposed in these errors. Unexpected programming exceptions propagate. Tests use fake clients and the real SDK with an in-memory transport; AI tests block socket connections and spend no API credits.

Future UI usage (this example makes a real request only when explicitly executed with configuration):

```python
from ai.analyzer import analyze_simulation
from ai.models import AIAnalysisError
from engine.simulator import simulate_scenario

result = simulate_scenario(decisions)
if result.valid:
    try:
        analysis = analyze_simulation(result)
    except AIAnalysisError as error:
        # Show a controlled explanation error; retain result's authoritative numbers.
        error_code = error.code
    else:
        explanation = analysis.summary
```

The frontend still needs explicit request triggering, loading/error states, and rendering of the five explanation fields alongside simulator numbers. No frontend files are changed here.

Documentation was checked against the official [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) and [Responses Python reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create). OpenAI Developer Docs MCP was not available in the session; official web documentation and the installed SDK signature were used instead.
