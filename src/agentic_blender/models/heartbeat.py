"""Heartbeat payload published by the Blender extension."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import AwareDatetime, Field, PositiveInt, field_validator

from agentic_blender.models.base import FrozenModel, utc_now
from agentic_blender.models.blender_version import BlenderVersion


class HeartbeatPayload(FrozenModel):
    """Liveness snapshot for the connected Blender process."""

    schema_version: Literal["1.0"] = "1.0"
    session_id: uuid.UUID
    blender_pid: PositiveInt
    timestamp: AwareDatetime = Field(default_factory=utc_now)
    # Accepts either a structured BlenderVersion object or a plain dotted
    # string (e.g. "5.2.0") sent by the Blender extension before the host
    # has had a chance to classify the version.
    blender_version: BlenderVersion

    @field_validator("blender_version", mode="before")
    @classmethod
    def _parse_blender_version_string(cls, value: object) -> object:
        """Coerce a plain dotted version string into a BlenderVersion."""
        if isinstance(value, str):
            parts = value.split(".")
            if len(parts) == 3:
                try:
                    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                    return BlenderVersion.classify(major, minor, patch)
                except ValueError:
                    pass
        return value
