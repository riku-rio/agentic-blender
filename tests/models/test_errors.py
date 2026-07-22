"""Tests for stable application errors."""

import json

import pytest

from agentic_blender.models import AppError, ErrorCode, ErrorDetail


@pytest.mark.unit
@pytest.mark.parametrize("code", list(ErrorCode))
def test_every_error_code_has_canonical_detail(code: ErrorCode) -> None:
    """Every stable code creates a complete canonical detail."""
    detail = ErrorDetail.for_code(code)

    assert detail.code is code
    assert detail.message
    assert detail.suggested_action


@pytest.mark.unit
@pytest.mark.parametrize("code", list(ErrorCode))
def test_error_detail_round_trip(code: ErrorCode) -> None:
    """Every error detail round-trips through JSON."""
    detail = ErrorDetail.for_code(
        code,
        context={"attempt": 1},
    )

    recovered = ErrorDetail.model_validate_json(detail.model_dump_json())
    assert recovered == detail


@pytest.mark.unit
def test_app_error_to_dict_is_json_compatible() -> None:
    """AppError returns string enum values and JSON-compatible context."""
    error = AppError(
        ErrorCode.OBJECT_NOT_FOUND,
        context={"object_name": "Cube"},
    )

    dumped = error.to_dict()
    encoded = json.dumps(dumped)

    assert dumped["code"] == "OBJECT_NOT_FOUND"
    assert "Cube" in encoded


@pytest.mark.unit
def test_from_exception_preserves_app_error() -> None:
    """Boundary conversion does not replace an existing AppError."""
    existing = AppError(ErrorCode.INVALID_SESSION)

    converted = AppError.from_exception(
        existing,
        fallback_code=ErrorCode.COMMAND_TIMEOUT,
    )

    assert converted is existing


@pytest.mark.unit
def test_from_exception_wraps_generic_error() -> None:
    """Boundary conversion gives a generic exception one stable code."""
    converted = AppError.from_exception(
        ValueError("bad value"),
        fallback_code=ErrorCode.INVALID_CONFIG,
    )

    assert converted.code is ErrorCode.INVALID_CONFIG
    assert converted.error.context["exception_type"] == "ValueError"
