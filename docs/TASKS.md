# Implementation roadmap

Current status: typed models, static data, validation, deterministic simulation, scoring, AI explanation, and the React/Vite frontend with FastAPI integration are implemented. The user confirmed a successful live AI smoke test; automated tests remain offline. Baseline Score is 52.55768; the reference scenario Score is 56.54307. The user explicitly confirmed subtraction of the critical penalty on 2026-09-23; see ARCHITECTURE.md for the clarification. PROJECT_SPEC.md is unchanged as requested. Visual review on target desktop sizes and comparison of separate scenarios remain future tasks.

## Phase 1 — Core simulation

* [x] Define typed project models
* [x] Add baseline district data
* [x] Add M1-M14 initiative data
* [x] Implement scenario validator
* [x] Implement lag scaling
* [x] Implement district effects
* [x] Implement city-wide effects
* [x] Implement synergies
* [x] Implement clipping
* [x] Implement district scoring
* [x] Implement D_avg
* [x] Implement N_crit
* [x] Implement final Score

## Phase 2 — Tests

* [x] Baseline regression = 52.55768
* [x] Reference scenario ≈ 56.54307
* [x] Budget validation
* [x] Decision count validation
* [x] Duplicate validation
* [x] Direction limit
* [x] District/city target validation
* [x] Incompatibility validation
* [x] Lag scaling tests
* [x] Synergy tests
* [x] Clipping tests
* [x] Order invariance test (validator and full simulation, including all 120 reference permutations)

## Phase 3 — UI

* [x] Scenario builder
* [x] Initiative selector
* [x] District selector
* [x] Budget counter
* [x] Validation feedback
* [x] Before/after visualization
* [x] Score visualization
* [x] District comparison
* [x] Explicit AI analysis with loading/error states
* [x] Session state, edit invalidation, demo preset and reset
* [x] Offline API/client tests and React reference-result rendering verification
* [ ] Visual browser review at 1366×768 and 1920×1080

## Phase 4 — AI

* [x] Structured SimulationResult payload for AI
* [x] Scenario explanation
* [x] Strengths
* [x] Risks
* [x] Trade-offs
* [x] Recommendations
* [ ] Scenario comparison

## Phase 5 — Optional hackathon features

* [ ] Team comparison
* [ ] Unexpected city events
* [ ] Scenario optimization
* [ ] Automatic presentation summary
