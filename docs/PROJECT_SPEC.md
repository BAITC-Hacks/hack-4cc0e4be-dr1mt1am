# Project specification — Akim for 5 Hours

All indicator values are in range 0-100, where higher is always better.

## District indicators

T1 — Transport — Road congestion relief
100 = no peak-hour traffic congestion

T2 — Transport — Public transport accessibility
100 = all residents within 500 m of a stop with service interval <= 10 minutes

E1 — Ecology — Greenery
100 = >=20 square meters of greenery per resident

E2 — Ecology — Air quality
100 = winter AQI <= 50
0 = chronic smog

S1 — Social infrastructure — Schools and kindergartens
100 = full normative demand covered, no second shift

S2 — Social infrastructure — Clinics and primary healthcare
100 = full per-capita standard achieved

B1 — Safety — Street safety
100 = lighting and cameras everywhere, minimum incidents

B2 — Safety — Road safety
100 = minimum injury-related traffic accidents

C1 — City services — Utility reliability
100 = no heating/water accidents during the year

C2 — City services — Resident request resolution speed
100 = all resident requests resolved on time

## District baseline data

```text
District: Esil
Population share: 0.27
T1 45
T2 62
E1 68
E2 72
S1 48
S2 55
B1 78
B2 60
C1 75
C2 70
Baseline district score D = 62.99
```

```text
District: Almaty
Population share: 0.24
T1 40
T2 75
E1 50
E2 55
S1 60
S2 65
B1 62
B2 52
C1 50
C2 60
Baseline district score D = 57.06
```

```text
District: Saryarka
Population share: 0.20
T1 50
T2 70
E1 42
E2 40
S1 62
S2 68
B1 58
B2 55
C1 45
C2 55
Baseline district score D = 54.65
```

```text
District: Baikonur
Population share: 0.13
T1 52
T2 68
E1 55
E2 50
S1 58
S2 60
B1 52
B2 58
C1 55
C2 58
Baseline district score D = 56.63
```

```text
District: Nura
Population share: 0.16
T1 55
T2 40
E1 45
E2 65
S1 38
S2 35
B1 55
B2 50
C1 60
C2 50
Baseline district score D = 49.18
```

## District profiles

Esil:
wealthier district, but bridge congestion and overcrowded schools.

Almaty:
old utility infrastructure and traffic congestion.

Saryarka:
smog caused by private-sector heating and weak greenery.

Baikonur:
balanced middle district with no extreme weaknesses.

Nura:
main underperformer in social infrastructure and public transport.

---

## Initiative catalog

Simulation horizon H = 8 quarters.

Realized fraction:

(8 - L) / 8

where L is the initiative lag in quarters.

Type "District":
requires one target district and affects only that district.

Type "City":
applies to all five districts.

The initiative catalog contains these 14 initiatives.

```text
M1
Direction: Transport
Name: Dedicated bus lanes
Type: District
Cost: 18
Lag: 2
Full effects:
T1 +6
T2 +9
```

```text
M2
Direction: Transport
Name: Smart traffic lights / adaptive traffic management
Type: City
Cost: 22
Lag: 2
Full effects:
T1 +4
B2 +3
```

```text
M3
Direction: Transport
Name: LRT line / expansion
Type: District
Cost: 30
Lag: 4
Full effects:
T1 +16
T2 +20
E2 +4
```

```text
M4
Direction: Ecology
Name: Park / public square
Type: District
Cost: 15
Lag: 2
Full effects:
E1 +12
E2 +3
B1 +2
```

```text
M5
Direction: Ecology
Name: Convert private-sector heating to clean fuel
Type: District
Cost: 25
Lag: 3
Full effects:
E2 +14
C1 +4
```

```text
M6
Direction: Ecology
Name: City greenery and windbreak program
Type: City
Cost: 20
Lag: 4
Full effects:
E1 +5
E2 +3
```

```text
M7
Direction: Social
Name: School + kindergarten modular construction
Type: District
Cost: 24
Lag: 3
Full effects:
S1 +16
```

```text
M8
Direction: Social
Name: Family health center / clinic
Type: District
Cost: 20
Lag: 3
Full effects:
S2 +14
```

```text
M9
Direction: Social
Name: Courtyard sports hubs
Type: District
Cost: 10
Lag: 1
Full effects:
S1 +3
S2 +3
B1 +3
```

```text
M10
Direction: Safety
Name: Lighting and cameras / Safe City expansion
Type: District
Cost: 12
Lag: 1
Full effects:
B1 +12
B2 +2
```

```text
M11
Direction: Safety
Name: Safe crossings and school zones
Type: District
Cost: 10
Lag: 1
Full effects:
B2 +12
T1 -2
```

```text
M12
Direction: Services
Name: Unified digital resident request platform
Type: City
Cost: 14
Lag: 1
Full effects:
C2 +5
```

```text
M13
Direction: Services
Name: Heating and water network modernization
Type: District
Cost: 28
Lag: 4
Full effects:
C1 +18
E2 +2
```

```text
M14
Direction: Services
Name: Emergency utility teams + early warning
Type: City
Cost: 16
Lag: 1
Full effects:
C1 +5
C2 +2
```

---

## Synergies

Synergy bonus applies if both initiatives are selected.

For district initiatives, the bonus is applied to the district of the FIRST initiative in the synergy pair.

Synergy bonuses are fixed and are NOT scaled by lag.

M1 + M2
Bonus:
T1 +2 in the district selected for M1

M10 + M12
Bonus:
B1 +2 in the district selected for M10

M5 + M6
Bonus:
E2 +2 in the district selected for M5

---

## Incompatibilities

M1 and M3:
cannot both be selected in the same scenario at all.
Either BRT or LRT.

M4 and M7:
cannot be selected in the same district.

M5 and M13:
cannot be selected in the same district.

---

## Scoring

For each district d and indicator k:

```text
I'_dk =
clip(
I_dk
+ sum(
effect_mk * (8 - L_m) / 8
)
+ synergy bonuses,
0,
100
)
```

District score:

D_d = sum(w_k * I'_dk)

Indicator weights:

T1 = 0.10
T2 = 0.10
E1 = 0.09
E2 = 0.11
S1 = 0.11
S2 = 0.11
B1 = 0.09
B2 = 0.09
C1 = 0.10
C2 = 0.10

Sum = 1.0

Direction-level total weights:

Transport = 0.20
Ecology = 0.20
Social = 0.22
Safety = 0.18
Services = 0.20

City population-weighted score:

D_avg = sum(population_share_d * D_d)

Critical count:

N_crit =
number of district × indicator pairs with final value STRICTLY LESS THAN 40.

Final Astana Quality of Life Score:

```text
Score =
0.7 * D_avg
+ 0.3 * min(D_d)

* 1.0 * N_crit
```

The minimum district component prevents optimizing only strong districts.

The critical-value penalty prevents leaving severe weaknesses unresolved.

---

## Baseline regression

Without initiatives:

D_avg = 56.8624

Minimum district score:
49.18

N_crit = 2

The critical values are:

Nura S1 = 38
Nura S2 = 35

Expected final Score:

52.55768

Display value:

52.56

---

## Reference valid scenario

Exactly these five decisions:

M7 -> Nura
M8 -> Nura
M10 -> Nura
M12 -> city
M5 -> Saryarka

Total cost:

95

M10 + M12 synergy must trigger.

Expected Score:

approximately 56.54307

Expected display:

56.54

Approximate improvement over baseline:

+3.99 / +4.0

---

## Validation rules

1. Budget is exactly 100 available units.

2. User must select exactly 5 initiatives.

3. Initiative IDs cannot repeat.

4. District initiative requires a district.

5. City initiative must not have a district.

6. Maximum 2 initiatives from the same direction.

7. All incompatibilities must be validated.

8. Invalid scenarios must not receive a Score.

9. Decision order does not affect the outcome.

10. Remaining budget gives no bonus and does not expire.

---

## AI responsibility

The LLM receives already-calculated information such as:

* score before
* score after
* district scores before/after
* indicator changes
* selected initiatives
* initiative contributions
* budget used
* remaining budget
* critical values
* triggered synergies

The LLM explains:

* strengths
* risks
* trade-offs
* consequences
* comparisons
* improvement suggestions

The LLM does not calculate the official numerical result.

## Scoring clarification required

The final Score expression above is preserved exactly as supplied. Its `* 1.0 * N_crit` line conflicts with the stated critical-value penalty and baseline regression. Using the supplied baseline terms, `0.7 * 56.8624 + 0.3 * 49.18 = 54.55768`; subtracting `1.0 * 2` gives the required `52.55768`.

The candidate correction is `Score = 0.7 * D_avg + 0.3 * min(D_d) - 1.0 * N_crit`. It requires explicit user confirmation before implementation; it is not an authorized replacement for the supplied expression. Preserve all supplied constants and regression targets while this discrepancy is unresolved.

## Precision and scenario semantics

Use full precision internally and round only for display. Accumulate applicable normal effects and fixed synergies before clipping final indicators to `[0, 100]`. The first initiative in a synergy pair means the first member listed above, not the user's decision order.

The no-initiative baseline is a scoring comparison fixture. User scenarios still require exactly five decisions, and invalid scenarios do not receive a Score. `city` in the reference scenario denotes city scope, not a district value.
