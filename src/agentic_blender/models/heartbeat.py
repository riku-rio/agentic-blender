"""Heartbeat payload published by the Blender extension."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, PositiveInt, StringConstraints

from agentic_blender.models.base import FrozenModel, utc_now

DottedVersion = Annotated[
    str,
    StringConstraints(pattern=r"^\d+\.\d+\.\d+$"),
]


class HeartbeatPayload(FrozenModel):
    """Liveness snapshot for the connected Blender process."""

    schema_version: Literal["1.0"] = "1.0"
    session_id: uuid.UUID
    blender_pid: PositiveInt
    timestamp: AwareDatetime = Field(default_factory=utc_now)
    blender_version: DottedVersion
