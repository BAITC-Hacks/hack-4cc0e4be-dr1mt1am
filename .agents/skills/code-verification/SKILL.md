---
name: code-verification
description: Use after changes to simulation logic, datasets, validation, scoring or integration to verify correctness.
---

# Code verification

Work from the repository root and follow this workflow:

1. Inspect `git diff` and `git diff --cached`; inspect `git status --short` and relevant untracked files so new files are included in the review.
2. Confirm the task did not modify unrelated files. Preserve pre-existing user changes; do not reset or discard them.
3. Read relevant rules in `docs/PROJECT_SPEC.md` and run the relevant tests using the repository's existing test tooling. If no suite exists, report it as unavailable, not passing.
4. Run the full engine suite when simulation behavior changes.
5. Verify the baseline regression: `52.55768` (display `52.56`). The baseline fixture does not bypass validation for user scenarios.
6. Verify the reference regression: `M7 -> Nura`, `M8 -> Nura`, `M10 -> Nura`, `M12 -> city`, `M5 -> Saryarka`; cost `95`; Score approximately `56.54307`; `M10 + M12` synergy triggered.
7. Check relevant edge cases: budget greater than 100; fewer/more than five decisions; duplicate initiative; more than two from one direction; district/city target rules; all incompatibilities; lag scaling; fixed synergies; clipping; and decision order invariance. Check that exactly 40 is not critical, invalid scenarios have no Score, and display rounding does not affect calculations.
8. Do not hide failures. Report specification contradictions and unexpected regression changes rather than silently changing rules or constants.
9. Do not weaken tests simply to make them pass.
10. Report files changed, tests run (commands), results, and remaining limitations, including unavailable tests or unresolved specification issues.
