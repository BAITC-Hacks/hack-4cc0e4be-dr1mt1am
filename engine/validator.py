"""Scenario validation only: no effects, simulation, or Score calculation."""

from collections import Counter, defaultdict
from collections.abc import Sequence

from .constants import BUDGET, MAX_INITIATIVES_PER_DIRECTION, REQUIRED_DECISION_COUNT
from .data import DISTRICTS, INCOMPATIBILITIES, INITIATIVES
from .models import (
    Decision, Direction, DistrictName, IncompatibilityScope, InitiativeId,
    InitiativeType, ValidationIssue, ValidationResult,
)


def validate_scenario(decisions: Sequence[Decision]) -> ValidationResult:
    """Validate typed decisions, including unknown string IDs and district names.

    Repeated selections each contribute to cost and direction counts. Unknown
    initiatives make both budget fields None, but do not stop independent checks.
    Issues are deduplicated and sorted by (code, message), regardless of input order.
    Raw JSON and objects outside the Decision interface are not parsed here.
    """
    issues: set[ValidationIssue] = set()
    counts = Counter(decision.initiative_id for decision in decisions)
    direction_counts: Counter[Direction] = Counter()
    targets: dict[InitiativeId, set[DistrictName]] = defaultdict(set)

    if len(decisions) != REQUIRED_DECISION_COUNT:
        issues.add(ValidationIssue(
            "INVALID_DECISION_COUNT",
            f"Нужно выбрать ровно {REQUIRED_DECISION_COUNT} мероприятий; "
            f"выбрано: {len(decisions)}.",
        ))

    for initiative_id, count in counts.items():
        if count > 1:
            issues.add(ValidationIssue(
                "DUPLICATE_INITIATIVE",
                f"Мероприятие {initiative_id} выбрано {count} раз; "
                "каждое мероприятие можно выбрать только один раз.",
            ))

    known_cost = 0
    all_ids_known = True
    for decision in decisions:
        initiative = INITIATIVES.get(decision.initiative_id)
        if initiative is None:
            all_ids_known = False
            issues.add(ValidationIssue(
                "UNKNOWN_INITIATIVE",
                f"Неизвестное мероприятие: {decision.initiative_id}.",
            ))
            continue

        known_cost += initiative.cost
        direction_counts[initiative.direction] += 1
        if initiative.type == InitiativeType.CITY:
            if decision.district is not None:
                issues.add(ValidationIssue(
                    "DISTRICT_NOT_ALLOWED",
                    f"Для городского мероприятия {initiative.id} район "
                    "не указывается; уберите выбор района.",
                ))
        elif decision.district is None:
            issues.add(ValidationIssue(
                "DISTRICT_REQUIRED",
                f"Для районного мероприятия {initiative.id} необходимо выбрать район.",
            ))
        elif decision.district not in DISTRICTS:
            issues.add(ValidationIssue(
                "UNKNOWN_DISTRICT",
                f"Неизвестный район {decision.district!r} для мероприятия {initiative.id}.",
            ))
        else:
            targets[initiative.id].add(decision.district)

    budget_used = known_cost if all_ids_known else None
    budget_remaining = BUDGET - budget_used if budget_used is not None else None
    if budget_used is not None and budget_used > BUDGET:
        issues.add(ValidationIssue(
            "BUDGET_EXCEEDED",
            f"Стоимость сценария {budget_used} превышает бюджет {BUDGET}.",
        ))

    for direction, count in direction_counts.items():
        if count > MAX_INITIATIVES_PER_DIRECTION:
            issues.add(ValidationIssue(
                "DIRECTION_LIMIT_EXCEEDED",
                f"В направлении «{direction.value}» выбрано {count} мероприятий; "
                f"допустимо не больше {MAX_INITIATIVES_PER_DIRECTION}.",
            ))

    for rule in INCOMPATIBILITIES:
        first, second = rule.first_initiative_id, rule.second_initiative_id
        if first not in counts or second not in counts:
            continue
        if rule.scope == IncompatibilityScope.SCENARIO:
            issues.add(ValidationIssue(
                "INCOMPATIBLE_INITIATIVES",
                f"Мероприятия {first} и {second} нельзя выбирать вместе "
                "в одном сценарии, даже для разных районов.",
            ))
        elif rule.scope == IncompatibilityScope.SAME_DISTRICT:
            for district in targets.get(first, set()) & targets.get(second, set()):
                issues.add(ValidationIssue(
                    "INCOMPATIBLE_INITIATIVES",
                    f"Мероприятия {first} и {second} несовместимы в районе {district}.",
                ))

    errors = sorted(issues, key=lambda issue: (issue.code, issue.message))
    return ValidationResult(
        valid=not errors,
        errors=errors,
        budget_used=budget_used,
        budget_remaining=budget_remaining,
    )
