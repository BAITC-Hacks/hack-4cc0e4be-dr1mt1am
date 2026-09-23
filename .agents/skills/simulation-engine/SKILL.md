---
name: simulation-engine
description: Use when implementing or modifying validation, initiative effects, lag scaling, synergies, incompatibilities, district scoring, or Astana Quality of Life Score.
---

# Simulation engine

Work from the repository root and follow this workflow:

1. Read `docs/PROJECT_SPEC.md`, including any unresolved clarification. Do not silently resolve a specification contradiction; obtain an explicit user decision before implementing the affected rule.
2. Determine whether the change belongs to `engine/validator.py`, `engine/simulator.py`, or `engine/scoring.py`; consult `docs/ARCHITECTURE.md` for boundaries.
3. Never change constants without explicit user instruction. Preserve the catalog, weights, costs, effects, lags, synergies, incompatibilities, and validation rules.
4. Keep the engine deterministic and independent of decision order, UI, and LLM access. Invalid scenarios must not receive a Score.
5. Scale normal effects with `(8 - lag) / 8` for the eight-quarter horizon. District effects affect exactly the selected district; city effects affect all five districts.
6. Apply fixed synergy bonuses without lag scaling. Target the district of the first initiative listed in the specification's synergy pair, not the first user selection.
7. Clip final indicators to `[0, 100]` after accumulating all applicable effects and synergies.
8. Use full precision internally.
9. Round only for presentation.
10. Add relevant tests for behavior changes and run regression tests, including baseline and reference scenarios. If tests do not exist yet, report that limitation rather than claiming a pass; create the relevant tests when implementing behavior.
11. Treat unexpected changes to baseline or reference values as bugs. Do not weaken tests or replace expected values to hide failures.

Regression anchors:

- Baseline = `52.55768` (display `52.56`). This is a no-initiative comparison fixture, not a valid user submission.
- Reference scenario: `M7 -> Nura`, `M8 -> Nura`, `M10 -> Nura`, `M12 -> city`, `M5 -> Saryarka`.
- Reference cost = `95`; Score approximately `56.54307` (display `56.54`). The `M10 + M12` synergy must trigger.
