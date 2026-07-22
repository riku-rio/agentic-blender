"""Saved Blender project result model."""

from __future__ import annotations

from pathlib import Path

from pydantic import AwareDatetime, Field, PositiveInt, field_validator

from agentic_blender.models.base import FrozenModel, utc_now
from agentic_blender.models.blender_version import BlenderVersion
from agentic_blender.models.scene import SceneSummary


class ExportResult(FrozenModel):
    """Validated result of saving the active project as a .blend file."""

    path: Path
    size_bytes: PositiveInt
    exported_at: AwareDatetime = Field(default_factory=utc_now)
    blender_version: BlenderVersion
    scene_summary: SceneSummary
    verified: bool

    @field_validator("path")
    @classmethod
    def _path_is_absolute_blend(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("export path must be absolute")

        if value.suffix.lower() != ".blend":
            raise ValueError("export path must use the .blend extension")

        return value
