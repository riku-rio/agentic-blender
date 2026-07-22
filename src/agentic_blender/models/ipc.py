"""Strict JSON-compatible IPC command and response envelopes."""

from __future__ import annotations

import enum
import uuid
from typing import Literal

from pydantic import AwareDatetime, Field, JsonValue, model_validator

from agentic_blender.models.base import FrozenModel, utc_now
from agentic_blender.models.errors import ErrorDetail


class CommandType(str, enum.Enum):
    """Allowlisted internal Blender-extension command types."""

    PING = "PING"
    GET_PROJECT_STATE = "GET_PROJECT_STATE"
    NEW_PROJECT = "NEW_PROJECT"
    DELETE_OBJECT = "DELETE_OBJECT"
    ADD_PRIMITIVE = "ADD_PRIMITIVE"
    INSPECT_SCENE = "INSPECT_SCENE"
    SAVE_BLEND = "SAVE_BLEND"


class CommandEnvelope(FrozenModel):
    """Command written by the external process for the Blender extension."""

    schema_version: Literal["1.0"] = "1.0"
    command_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    command_type: CommandType
    session_id: uuid.UUID
    issued_at: AwareDatetime = Field(default_factory=utc_now)
    payload: dict[str, JsonValue] = Field(default_factory=dict)


class ResponseStatus(str, enum.Enum):
    """Command response outcome."""

    OK = "OK"
    ERROR = "ERROR"


class ResponseEnvelope(FrozenModel):
    """Response written by the Blender extension."""

    schema_version: Literal["1.0"] = "1.0"
    command_id: uuid.UUID
    command_type: CommandType
    session_id: uuid.UUID
    status: ResponseStatus
    responded_at: AwareDatetime = Field(default_factory=utc_now)
    payload: dict[str, JsonValue] = Field(default_factory=dict)
    error: ErrorDetail | None = None

    @model_validator(mode="after")
    def _status_matches_error(self) -> ResponseEnvelope:
        if self.status is ResponseStatus.ERROR and self.error is None:
            raise ValueError("error is required when status is ERROR")

        if self.status is ResponseStatus.OK and self.error is not None:
            raise ValueError("error must be omitted when status is OK")

        return self
