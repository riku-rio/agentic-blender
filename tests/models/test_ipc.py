"""IPC envelope validation tests."""

import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from agentic_blender.models import (
    CommandEnvelope,
    CommandType,
    ErrorCode,
    ErrorDetail,
    ResponseEnvelope,
    ResponseStatus,
)


@pytest.mark.unit
@pytest.mark.parametrize("command_type", list(CommandType))
def test_command_type_round_trip(command_type: CommandType) -> None:
    """Every allowlisted command type round-trips through JSON."""
    command = CommandEnvelope(
        command_type=command_type,
        session_id=uuid.uuid4(),
    )

    recovered = CommandEnvelope.model_validate_json(command.model_dump_json())

    assert recovered == command


@pytest.mark.unit
def test_unknown_command_type_is_rejected() -> None:
    """Unknown command strings are rejected by model validation."""
    raw = '{"command_type":"EXECUTE_PYTHON","session_id":"00000000-0000-0000-0000-000000000001"}'

    with pytest.raises(ValidationError):
        CommandEnvelope.model_validate_json(raw)


@pytest.mark.unit
def test_payload_rejects_non_json_values() -> None:
    """Payloads cannot contain arbitrary Python objects."""
    with pytest.raises(ValidationError):
        CommandEnvelope(
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            payload={"path": Path("not-json")},
        )


@pytest.mark.unit
def test_error_response_requires_error_detail() -> None:
    """ERROR responses require one structured error."""
    with pytest.raises(ValidationError):
        ResponseEnvelope(
            command_id=uuid.uuid4(),
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            status=ResponseStatus.ERROR,
        )


@pytest.mark.unit
def test_ok_response_rejects_error_detail() -> None:
    """OK responses cannot contain an error payload."""
    with pytest.raises(ValidationError):
        ResponseEnvelope(
            command_id=uuid.uuid4(),
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            status=ResponseStatus.OK,
            error=ErrorDetail.for_code(ErrorCode.COMMAND_TIMEOUT),
        )
