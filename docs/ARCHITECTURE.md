# Architecture

The deterministic engine is authoritative for every numerical result. Business rules and constants live in [PROJECT_SPEC.md](PROJECT_SPEC.md); implementation priorities live in [TASKS.md](TASKS.md).

```text
User selections
-> Validator
-> Simulation Engine
-> Scoring Engine
-> structured SimulationResult
-> AI Analyzer
-> UI
```

| Component / expected location | Responsibility |
| --- | --- |
| User selections / `ui/` | Collect initiative IDs and district targets, display budget and validation feedback, and submit decisions to the validator. |
| Validator / `engine/validator.py` | Enforce budget, exactly five decisions, uniqueness, direction limits, target rules, and incompatibilities. Return actionable validation errors for invalid scenarios; do not pass them to simulation or scoring. |
| Simulation Engine / `engine/simulator.py` | Starting from baseline data, apply normal lag-scaled effects to district or city targets, add fixed synergy bonuses, then clip final indicators. Be deterministic and independent of decision order. |
| Scoring Engine / `engine/scoring.py` | Calculate district scores, population-weighted `D_avg`, `N_crit`, and the final Astana Quality of Life Score from calculated indicators using the specification. Preserve full precision. |
| Structured `SimulationResult` / `engine/models.py` | Carry validation, budget used/remaining, independent before/after indicator snapshots, district scores, population-weighted averages, weakest districts and minimum scores, critical counts, final scores and delta, and triggered synergies with their target districts. Invalid scenarios have `None` for all simulation and score fields. |
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

Typed domain models, static data, validation, simulation, scoring, and their tests are implemented. `validate_scenario(decisions: Sequence[Decision]) -> ValidationResult` returns Russian error messages with stable codes, plus budget used/remaining (both `None` for unknown initiative IDs). Repeated selections each count toward cost and direction limits. Errors are deduplicated and sorted by code and message, independent of decision order. AI and UI remain unimplemented.

## Simulation API

`simulate_scenario(decisions: Sequence[Decision]) -> SimulationResult` calls the existing validator once. Invalid input returns immediately, before copying baseline or performing any scoring. Valid input creates independent before/after snapshots, applies normal effects in initiative-ID order, applies each selected synergy once, then clips and scores. No rounding occurs in the engine. Equal weakest-district scores are resolved alphabetically by district identifier.

The result dataclass is frozen; its nested snapshot dictionaries are independent copies, not shared static data. Consumers can access all requested before/after values directly. `triggered_synergies` contains `TriggeredSynergy(synergy, district)` records referring to the immutable catalog definitions.

## Confirmed scoring clarification

On 2026-09-23 the user explicitly confirmed:

```text
Score = 0.7 * D_avg + 0.3 * min(D_d) - 1.0 * N_crit
```

The supplied specification's `* 1.0 * N_crit` line was inconsistent with its stated penalty and regression values. The unpenalized baseline is 54.55768; subtracting two critical pairs gives 52.55768. The reference scenario has zero critical pairs and yields 56.54307. The implementation follows this explicit user clarification. PROJECT_SPEC.md itself remains unchanged at the user's request.
