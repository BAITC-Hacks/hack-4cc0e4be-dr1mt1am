# Implementation roadmap

Current status: typed models, static data, validation, deterministic simulation, scoring, and the AI explanation adapter are implemented and tested. AI tests are offline; live answer quality and model access have not been evaluated. Baseline Score is 52.55768; the reference scenario Score is 56.54307. The user explicitly confirmed subtraction of the critical penalty on 2026-09-23; see ARCHITECTURE.md for the clarification. PROJECT_SPEC.md is unchanged as requested. UI integration and scenario comparison remain future tasks.

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

* [ ] Scenario builder
* [ ] Initiative selector
* [ ] District selector
* [ ] Budget counter
* [ ] Validation feedback
* [ ] Before/after visualization
* [ ] Score visualization
* [ ] District comparison

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
