"""Workflow model tests."""

import pytest
from pydantic import ValidationError

from agentic_blender.models import WorkflowState, WorkflowStatus


@pytest.mark.unit
def test_required_prd_states_exist() -> None:
    """The shared state enum contains every public PRD state."""
    required = {
        "READY",
        "PLANNING",
        "PLAN_REVIEW",
        "IMPLEMENTING",
        "VERIFYING_STATE",
        "CAPTURING_SCREENSHOT",
        "VISUAL_REVIEW",
        "FIXING",
        "EXPORTING",
        "COMPLETED",
        "FAILED",
        "DISCONNECTED",
    }

    assert required <= {state.value for state in WorkflowState}


@pytest.mark.unit
def test_attempt_cannot_exceed_limit() -> None:
    """Bounded workflow loops reject impossible counters."""
    with pytest.raises(ValidationError):
        WorkflowStatus(
            state=WorkflowState.PLAN_REVIEW,
            attempt=4,
            max_attempts=3,
        )


@pytest.mark.unit
def test_failed_state_requires_reason() -> None:
    """A failed workflow cannot omit its failure reason."""
    with pytest.raises(ValidationError):
        WorkflowStatus(state=WorkflowState.FAILED)
