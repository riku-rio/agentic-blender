"""Session metadata models."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import AwareDatetime, Field, PositiveInt

from agentic_blender.models.base import FrozenModel, utc_now


class SessionMetadata(FrozenModel):
    """Metadata for one external-server to Blender-extension session."""

    schema_version: Literal["1.0"] = "1.0"
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    blender_pid: PositiveInt
    created_at: AwareDatetime = Field(default_factory=utc_now)
    last_heartbeat_at: AwareDatetime = Field(default_factory=utc_now)
