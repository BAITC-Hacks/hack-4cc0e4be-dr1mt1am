# Implementation roadmap

Current status: typed domain models, static project data, and the scenario validator are implemented, with data integrity and validator tests. Next is simulation when requested; simulation, scoring, UI, and AI remain unimplemented. Add relevant Phase 2 tests alongside behavior changes. Resolve the scoring clarification in PROJECT_SPEC.md before implementing the final Score.

## Phase 1 — Core simulation

* [x] Define typed project models
* [x] Add baseline district data
* [x] Add M1-M14 initiative data
* [x] Implement scenario validator
* [ ] Implement lag scaling
* [ ] Implement district effects
* [ ] Implement city-wide effects
* [ ] Implement synergies
* [ ] Implement clipping
* [ ] Implement district scoring
* [ ] Implement D_avg
* [ ] Implement N_crit
* [ ] Implement final Score

## Phase 2 — Tests

* [ ] Baseline regression = 52.55768
* [ ] Reference scenario ≈ 56.54307
* [x] Budget validation
* [x] Decision count validation
* [x] Duplicate validation
* [x] Direction limit
* [x] District/city target validation
* [x] Incompatibility validation
* [ ] Lag scaling tests
* [ ] Synergy tests
* [ ] Clipping tests
* [ ] Order invariance test (validator covered, including all 120 reference permutations; simulation pending)

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
