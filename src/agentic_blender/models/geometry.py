"""Geometric values used by scene inspection and modeling commands."""

from __future__ import annotations

from pydantic import Field

from agentic_blender.models.base import FrozenModel


class Vector3(FrozenModel):
    """Three-dimensional vector."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Transform(FrozenModel):
    """Object transform using Euler XYZ rotation in radians."""

    location: Vector3 = Field(default_factory=Vector3)
    rotation: Vector3 = Field(default_factory=Vector3)
    scale: Vector3 = Field(default_factory=lambda: Vector3(x=1.0, y=1.0, z=1.0))
