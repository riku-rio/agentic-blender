"""Stable application errors shared by CLI, MCP, IPC, and internal services."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Final

from pydantic import Field, JsonValue

from agentic_blender.models.base import FrozenModel

if TYPE_CHECKING:
    from collections.abc import Mapping


class ErrorCode(str, enum.Enum):
    """Stable error codes serialized across all external boundaries."""

    BLENDER_NOT_FOUND = "BLENDER_NOT_FOUND"
    BLENDER_UNSUPPORTED_VERSION = "BLENDER_UNSUPPORTED_VERSION"
    BLENDER_NOT_CONNECTED = "BLENDER_NOT_CONNECTED"
    BLENDER_START_TIMEOUT = "BLENDER_START_TIMEOUT"
    BLENDER_DISCONNECTED = "BLENDER_DISCONNECTED"
    UNSAVED_CHANGES = "UNSAVED_CHANGES"
    OBJECT_NOT_FOUND = "OBJECT_NOT_FOUND"
    UNSUPPORTED_PRIMITIVE = "UNSUPPORTED_PRIMITIVE"
    INVALID_OUTPUT_PATH = "INVALID_OUTPUT_PATH"
    OUTPUT_ALREADY_EXISTS = "OUTPUT_ALREADY_EXISTS"
    SCREENSHOT_FAILED = "SCREENSHOT_FAILED"
    EXPORT_FAILED = "EXPORT_FAILED"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    INVALID_SESSION = "INVALID_SESSION"

    # Phase 1 additions required for semantically correct failures.
    INVALID_CONFIG = "INVALID_CONFIG"
    RUNTIME_PATH_ERROR = "RUNTIME_PATH_ERROR"


_CANONICAL_DETAILS: Final[dict[ErrorCode, tuple[str, str]]] = {
    ErrorCode.BLENDER_NOT_FOUND: (
        "No supported Blender installation was found.",
        "Install Blender 5.2.0 LTS or configure the Blender executable path.",
    ),
    ErrorCode.BLENDER_UNSUPPORTED_VERSION: (
        "The detected Blender version is not supported.",
        "Use Blender 5.2.0 LTS or run diagnostics for an unverified version.",
    ),
    ErrorCode.BLENDER_NOT_CONNECTED: (
        "The selected Blender process is not connected to Agentic Blender.",
        "Enable the extension, run agentic-blender doctor, and retry open_blender.",
    ),
    ErrorCode.BLENDER_START_TIMEOUT: (
        "Blender did not become ready before the startup timeout expired.",
        "Check Blender startup, extension enablement, and the configured startup timeout.",
    ),
    ErrorCode.BLENDER_DISCONNECTED: (
        "Blender disconnected while an operation was active.",
        "Confirm Blender is running, then start a new workflow with open_blender.",
    ),
    ErrorCode.UNSAVED_CHANGES: (
        "The active Blender project contains unsaved changes.",
        "Save the project or explicitly authorize discarding the changes.",
    ),
    ErrorCode.OBJECT_NOT_FOUND: (
        "The requested Blender object was not found.",
        "Call inspect_scene and verify the exact object name.",
    ),
    ErrorCode.UNSUPPORTED_PRIMITIVE: (
        "The requested primitive type is not supported.",
        "Use cube, sphere, icosphere, cylinder, cone, torus, plane, circle, triangle, or square.",
    ),
    ErrorCode.INVALID_OUTPUT_PATH: (
        "The requested output path is invalid or not writable.",
        "Provide an absolute writable output directory and a valid filename.",
    ),
    ErrorCode.OUTPUT_ALREADY_EXISTS: (
        "An artifact already exists at the requested output path.",
        "Choose a different path or explicitly allow overwrite.",
    ),
    ErrorCode.SCREENSHOT_FAILED: (
        "The Blender application screenshot could not be captured.",
        "Confirm the correct Blender window is visible and retry.",
    ),
    ErrorCode.EXPORT_FAILED: (
        "The Blender project could not be saved.",
        "Check the destination, available disk space, and Blender connection.",
    ),
    ErrorCode.COMMAND_TIMEOUT: (
        "The Blender command did not complete before its timeout expired.",
        "Check Blender responsiveness or increase the configured command timeout.",
    ),
    ErrorCode.INVALID_SESSION: (
        "The session identifier is invalid, expired, or no longer active.",
        "Start a new workflow with open_blender.",
    ),
    ErrorCode.INVALID_CONFIG: (
        "The Agentic Blender configuration is invalid.",
        "Correct or remove the invalid config.toml file, then run agentic-blender doctor.",
    ),
    ErrorCode.RUNTIME_PATH_ERROR: (
        "An Agentic Blender runtime directory could not be created or written.",
        "Check permissions for the current user's application-data directories.",
    ),
}


class ErrorDetail(FrozenModel):
    """Serializable structured error returned across application boundaries."""

    code: ErrorCode
    message: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)
    context: dict[str, JsonValue] = Field(default_factory=dict)

    @classmethod
    def for_code(
        cls,
        code: ErrorCode,
        *,
        context: Mapping[str, JsonValue] | None = None,
    ) -> ErrorDetail:
        """Create the canonical detail for an error code."""
        message, suggested_action = _CANONICAL_DETAILS[code]
        return cls(
            code=code,
            message=message,
            suggested_action=suggested_action,
            context=dict(context or {}),
        )


class AppError(Exception):
    """Internal exception carrying one stable structured application error."""

    def __init__(
        self,
        code: ErrorCode,
        *,
        context: Mapping[str, JsonValue] | None = None,
    ) -> None:
        """Initialize with a stable error code and optional context."""
        self.error = ErrorDetail.for_code(code, context=context)
        super().__init__(self.error.message)

    @property
    def code(self) -> ErrorCode:
        """Return the stable error code."""
        return self.error.code

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible dictionary."""
        dumped = self.error.model_dump(mode="json")
        return dict(dumped)

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        *,
        fallback_code: ErrorCode,
        context: Mapping[str, JsonValue] | None = None,
    ) -> AppError:
        """Preserve AppError or wrap another exception at an application boundary."""
        if isinstance(exc, cls):
            return exc

        merged_context: dict[str, JsonValue] = dict(context or {})
        merged_context.setdefault("exception_type", type(exc).__name__)

        if str(exc):
            merged_context.setdefault("reason", str(exc))

        return cls(fallback_code, context=merged_context)
