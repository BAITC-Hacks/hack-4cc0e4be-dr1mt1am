---
name: ai-analysis
description: Use when implementing AI-generated scenario explanation, comparison or recommendations using already-calculated simulator output.
---

# AI analysis

Read `docs/PROJECT_SPEC.md` and `docs/ARCHITECTURE.md` before changing the AI layer. `ai/analyzer.py` consumes an authoritative, already-calculated `SimulationResult`.

The LLM is not a calculator. It receives authoritative simulation values and may explain score changes, indicator changes, strengths, weaknesses, risks, trade-offs, recommendations, and comparisons between already-calculated scenarios.

It must not calculate the official Score, alter simulator numbers, invent numbers, costs, indicators, or selected initiatives, or assume missing data. If information is unavailable, say it is unavailable rather than inventing it. Recommendations may suggest a new scenario, but its numerical outcome must come from the deterministic engine before being presented as a simulator fact.

## Structured input

Prefer structured input with before/after scores, district scores and indicator changes, selected initiatives, initiative contributions, budget used/remaining, critical values, and triggered synergies.

Illustrative input shape (not a complete reference-scenario payload; empty collections below demonstrate structure and must not be interpreted as actual reference-scenario facts):

```json
{
  "score_before": 52.55768,
  "score_after": 56.54307,
  "budget_used": 95,
  "budget_remaining": 5,
  "selected_initiatives": [],
  "district_changes": {},
  "critical_values": [],
  "synergies_triggered": []
}
```

Populate real payloads from the engine. Preserve full precision in structured values; round only when presenting them. An invalid scenario has no Score and must not receive an invented result or explanation implying successful simulation.

## Explanation structure

Clearly distinguish:

- **Simulator facts:** supplied values, selected initiatives, and calculated changes.
- **Analysis:** interpretations of those facts, including strengths, weaknesses, risks, and trade-offs.
- **Recommendations:** suggested actions, explicitly identifying outcomes that require a new simulation.

For comparisons, require calculated outputs for each scenario. Verify that generated explanations preserve the provided values and clearly state missing information.
