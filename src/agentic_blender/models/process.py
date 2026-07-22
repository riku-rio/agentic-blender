"""Blender process and top-level window identity models."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, PositiveInt, field_validator

from agentic_blender.models.base import FrozenModel
from agentic_blender.models.blender_version import BlenderVersion


class WindowIdentity(FrozenModel):
    """Windows top-level Blender window identity."""

    hwnd: PositiveInt
    title: str = Field(min_length=1)


class BlenderProcess(FrozenModel):
    """Validated identity for one running Blender process."""

    pid: PositiveInt
    executable: Path
    version: BlenderVersion
    window: WindowIdentity | None = None

    @field_validator("executable")
    @classmethod
    def _executable_is_absolute(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("executable must be an absolute path")
        return value
