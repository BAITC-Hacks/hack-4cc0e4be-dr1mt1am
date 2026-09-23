# Implementation roadmap

Current status: typed models, static data, validation, deterministic simulation, and scoring are implemented and tested. Baseline Score is 52.55768; the reference scenario Score is 56.54307. The user explicitly confirmed subtraction of the critical penalty on 2026-09-23; see ARCHITECTURE.md for the clarification. PROJECT_SPEC.md is unchanged as requested. UI and AI remain unimplemented and require a separate task.

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

* [ ] Structured SimulationResult payload for AI
* [ ] Scenario explanation
* [ ] Strengths
* [ ] Risks
* [ ] Trade-offs
* [ ] Recommendations
* [ ] Scenario comparison

## Phase 5 — Optional hackathon features

* [ ] Team comparison
* [ ] Unexpected city events
* [ ] Scenario optimization
* [ ] Automatic presentation summary
