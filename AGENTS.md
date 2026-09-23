# Akim for 5 Hours

## Project and source of truth

“Akim for 5 Hours” is an AI-powered urban management simulator. The user receives a fixed virtual budget and selects exactly five urban initiatives. The deterministic engine calculates all numerical results; the LLM explains those results and is never the source of truth for numbers.

- [PROJECT_SPEC.md](docs/PROJECT_SPEC.md): formulas, datasets, business rules, costs, effects, lags, synergies, incompatibilities, and validation rules.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): component boundaries.
- [TASKS.md](docs/TASKS.md): implementation order and current priorities.

If code and PROJECT_SPEC.md disagree, the specification wins unless the user explicitly changes it. Never silently alter specification constants. Surface specification contradictions and obtain clarification before implementing the affected rule; do not change regression targets to conceal a discrepancy.

## Architecture boundaries

Keep validation, simulation, scoring, AI explanation, and UI separate:

| Expected owner | Responsibility |
| --- | --- |
| `engine/validator.py` | Validate user decisions. |
| `engine/simulator.py` | Apply initiative effects, lag scaling, city/district effects, synergies, and clipping. |
| `engine/scoring.py` | Calculate district scores and the final Astana Quality of Life Score. |
| `ai/analyzer.py` | Explain an already-calculated `SimulationResult`. |
| `ui/` | Collect input and display data. |

The UI must not duplicate scoring formulas. The AI layer must not calculate the authoritative Score.

## Validation and simulation

- Budget: 100; exactly 5 decisions; each initiative selected at most once.
- Maximum 2 initiatives from the same direction.
- District initiatives require exactly one district; city initiatives must have no district.
- Enforce every incompatibility in PROJECT_SPEC.md.
- Invalid scenarios receive no Score. Decision order must not affect the result.
- Horizon `H = 8` quarters. Scale normal effects by `realized_fraction = (8 - L) / 8`.
- Synergy bonuses are fixed and never lag-scaled. “First initiative” means the first member of the specification's synergy pair, not selection order.
- Clip final indicators to `[0, 100]` after accumulating effects and synergies.
- Use full precision internally; round only for display.

## Regression values

- Baseline final Score: `52.55768` (display `52.56`). The baseline is a scoring fixture without initiatives, not an exception allowing an invalid user scenario to receive a Score.
- Reference: `M7 -> Nura`, `M8 -> Nura`, `M10 -> Nura`, `M12 -> city`, `M5 -> Saryarka`.
- Reference cost: `95`; final Score approximately `56.54307` (display `56.54`).

Treat unexpected regression changes as bugs. Consult the specification's scoring clarification before implementing the final formula.

## AI rules

The LLM may explain changes, strengths, weak areas, and trade-offs; compare already-calculated scenarios; and make recommendations. It must not invent numbers, costs, indicators, or selected initiatives; calculate the official Score; alter simulation results; or assume missing data. State when information is unavailable.

## Coding and testing

Prefer small pure functions, type hints, dataclasses or typed models where useful, descriptive names, deterministic behavior, and testable business logic. Avoid overengineering. Do not introduce a database unless explicitly required later or add frameworks merely because they are popular.

Changes affecting simulation behavior must include relevant tests. Required categories:

- Baseline Score and reference scenario Score.
- Budget greater than 100.
- Fewer than 5 and more than 5 decisions.
- Duplicate initiative and more than 2 initiatives from one direction.
- Missing district for a district initiative and district supplied for a city initiative.
- Incompatibility validation, lag scaling, synergy application, clipping, and order invariance.

Never weaken tests simply to make them pass. Do not report tests as passing when the suite does not yet exist.

## Reusable skills

Use the relevant repository skill for its matching work:

- `.agents/skills/simulation-engine/SKILL.md`: validation, simulation, and scoring changes.
- `.agents/skills/code-verification/SKILL.md`: verification after logic, data, validation, scoring, or integration changes.
- `.agents/skills/ai-analysis/SKILL.md`: explanations, comparisons, and recommendations from calculated results.

## Git, security, and working method

Never commit `.env`, API keys, tokens, passwords, or credentials. Prefer focused changes and focused commits, for example:

```text
feat: implement scenario validator
feat: add lag-scaled initiative effects
test: add baseline score regression
fix: apply synergy after lag scaling
docs: document simulation architecture
```

For substantial changes: inspect relevant files, identify the correct layer, make the smallest coherent change, run relevant tests, and report what changed. Preserve unrelated user files and working code. Do not initialize another Git repository or commit or push unless explicitly asked.

The initial setup task is documentation and skills only: create the requested empty application directories, but no application logic, implementation placeholders, packages, databases, frameworks, Docker, or CI/CD. Future implementation follows TASKS.md when requested.
