"""Validate transport shape only. Scenario business validation belongs to engine."""

from pydantic import BaseModel, ConfigDict

from engine.models import Decision


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    # Unknown string IDs must reach the engine's structured validation.
    initiative_id: str
    district: str | None = None


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    decisions: list[DecisionRequest]

    def to_decisions(self) -> tuple[Decision, ...]:
        return tuple(Decision(item.initiative_id, item.district) for item in self.decisions)
