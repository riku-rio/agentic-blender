"""Geometry model tests."""

import math

import pytest
from pydantic import ValidationError

from agentic_blender.models import Transform, Vector3


@pytest.mark.unit
def test_transform_defaults() -> None:
    """Transform defaults to origin, zero rotation, and unit scale."""
    transform = Transform()

    assert transform.location == Vector3()
    assert transform.rotation == Vector3()
    assert transform.scale == Vector3(x=1.0, y=1.0, z=1.0)


@pytest.mark.unit
@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_vector_rejects_non_finite_values(invalid: float) -> None:
    """IPC vectors cannot contain non-finite JSON numbers."""
    with pytest.raises(ValidationError):
        Vector3(x=invalid)
