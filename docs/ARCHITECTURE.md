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
| Structured `SimulationResult` | Carry authoritative before/after scores, district scores, indicator changes, selected initiatives and contributions, budget used/remaining, critical values, and triggered synergies. Define this result model when implementing simulation and scoring; it is not implemented yet. |
| AI Analyzer / `ai/analyzer.py` | Consume structured calculated output and explain strengths, weaknesses, risks, trade-offs, comparisons, and recommendations. Clearly distinguish facts from analysis and recommendations. |
| Results UI / `ui/` | Display calculated values and explanations, before/after views, and district comparisons. Round only for presentation. |
| Domain models / `engine/models.py` | Frozen typed records for districts, initiatives, effects, decisions, synergies, incompatibilities, and indicator metadata. These records do not execute validation or simulation rules. |
| Static data / `engine/data.py`, `engine/constants.py` | Hold baseline districts, population shares, indicator weights, initiative catalog, synergies, incompatibilities, and constants exactly as specified. Python modules are authoritative at this stage; `data/` is reserved for possible future file assets. |
| Tests / `tests/` | Cover validation, simulation, scoring, baseline/reference regressions, and order invariance. |

## Boundaries

- No scoring logic in the UI; consume engine output instead of duplicating formulas.
- No official scoring in AI; the analyzer must not change or fabricate simulator values.
- Simulation and scoring must remain usable and testable without UI or LLM access.
- Invalid scenarios receive validation feedback and no Score. Baseline scoring is a separate comparison fixture, not a valid zero-decision user scenario.
- In a synergy pair, the first initiative is the first member listed in the specification, independent of user selection order.
- Resolve the specification's scoring clarification before implementing the final Score; preserve the supplied regression targets.

Typed domain models, static data, and data integrity tests are implemented. Validation, simulation, scoring, AI, and UI paths describe future ownership and are not implemented yet.
