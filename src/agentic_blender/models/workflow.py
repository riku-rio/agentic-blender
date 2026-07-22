"""Agent workflow status models displayed by the Blender extension."""

from __future__ import annotations

import enum
from typing import Final

from pydantic import AwareDatetime, Field, NonNegativeInt, PositiveInt, model_validator

from agentic_blender.models.base import FrozenModel, utc_now

DEFAULT_MAX_ATTEMPTS: Final[int] = 3
"""Policy default for workflow retry limit; also used by WorkflowConfig."""


class WorkflowState(str, enum.Enum):
    """Public and internal workflow states for v0.1.0."""

    IDLE = "IDLE"
    BLENDER_STARTING = "BLENDER_STARTING"
    READY = "READY"
    PLANNING = "PLANNING"
    PLAN_REVIEW = "PLAN_REVIEW"
    IMPLEMENTING = "IMPLEMENTING"
    VERIFYING_STATE = "VERIFYING_STATE"
    CAPTURING_SCREENSHOT = "CAPTURING_SCREENSHOT"
    VISUAL_REVIEW = "VISUAL_REVIEW"
    FIXING = "FIXING"
    EXPORTING = "EXPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DISCONNECTED = "DISCONNECTED"


class WorkflowStatus(FrozenModel):
    """Snapshot consumed by the Blender workflow-status UI."""

    state: WorkflowState
    task_summary: str | None = Field(default=None, max_length=500)
    current_step: str | None = Field(default=None, max_length=500)
    attempt: NonNegativeInt = 0
    max_attempts: PositiveInt = DEFAULT_MAX_ATTEMPTS
    last_action: str | None = Field(default=None, max_length=500)
    failure_reason: str | None = Field(default=None, max_length=2000)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _attempt_is_within_limit(self) -> WorkflowStatus:
        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot be greater than max_attempts")

        if self.state is WorkflowState.FAILED and not self.failure_reason:
            raise ValueError("failure_reason is required when state is FAILED")

        return self
