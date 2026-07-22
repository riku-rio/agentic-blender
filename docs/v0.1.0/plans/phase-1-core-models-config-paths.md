# Phase 1 Implementation Plan — Core Models, Configuration, and Runtime Paths

## Document Status

- **Tasks covered:** CORE-001–CORE-003, CFG-001–CFG-009, PATH-001–PATH-008, MOD-001–MOD-014, ERR-001–ERR-005
- **Phase:** 1.1 Package Structure · 1.2 Configuration · 1.3 Application Paths · 1.4 Shared Models · 1.5 Error System
- **Date:** 2026-07-22
- **Source tasks:** [TASKS.md §1.1–1.5](../TASKS.md)
- **Target branch:** `feat/phase-1-core`
- **Official environment:** Windows 10/11 x64 · Blender 5.2.0 LTS · Python 3.10+
- **Prerequisite:** Phase 0.2 and Phase 0.3 are merged and all Phase 0 quality checks pass.

---

## 1. Overview

This plan translates Phase 1 into an ordered implementation for the shared foundation used by every later phase.

It establishes:

- The package hierarchy consumed by Blender discovery, IPC, CLI, MCP, screenshot, and extension-packaging layers.
- A single package-version source based on installed distribution metadata.
- Stable, structured error codes and error payloads.
- Strict Pydantic models for sessions, workflow state, IPC envelopes, scene inspection, screenshots, and Blender project export.
- Deterministic per-user application paths using `platformdirs`.
- Safe creation and writability checks for runtime directories.
- A TOML configuration model with explicit precedence:
  1. Direct constructor overrides supplied by CLI code.
  2. Environment variables.
  3. The user TOML configuration file.
  4. Model defaults.
- Atomic TOML configuration persistence.
- Unit and integration tests for serialization, validation, paths, configuration, and errors.

This plan does **not** implement:

- Blender installation discovery.
- Running-process discovery.
- Blender launching.
- File IPC polling or command processing.
- Blender extension behavior.
- MCP server registration.
- User-facing CLI commands.
- Screenshot capture.
- Blender project saving.

Those behaviors belong to later phases.

### 1.1 Design Rules

The implementation must follow these rules:

1. Public shared models use strict field validation and reject unknown fields.
2. Pydantic models are frozen at the attribute level, but the implementation must not claim that every model is hashable or deeply immutable.
3. IPC payloads accept JSON-compatible values only.
4. All serialized datetimes must be timezone-aware.
5. Session and command identifiers use UUIDs to prevent malformed identifiers and path traversal.
6. User-facing output paths and internal runtime paths use different error codes.
7. The Phase 1 workflow and result models must match the v0.1.0 PRD terminology.
8. Blender 5.2.0 LTS is the only automatically supported Blender version in Phase 1. Later versions remain unverified until explicitly approved.
9. The external package must not import `bpy`, `mathutils`, or other Blender-embedded modules.
10. Secrets must not be stored in the long-lived application configuration.

### 1.2 Exit Criteria

Phase 1 is complete when:

- [ ] `src/agentic_blender/` contains the eight planned top-level sub-packages and the nested `platform/windows/` package.
- [ ] Every created package directory contains an `__init__.py`.
- [ ] `agentic_blender.__version__` is derived from installed package metadata.
- [ ] Stable error codes and structured error payloads are available to later boundaries.
- [ ] All shared models reject unknown fields and round-trip through JSON.
- [ ] Session and command identifiers reject malformed UUID values.
- [ ] Workflow states and workflow-status fields match the PRD.
- [ ] Scene, screenshot, and export result models contain all v0.1.0 verification fields.
- [ ] Configuration loads from TOML and environment variables with tested precedence.
- [ ] Configuration saves atomically as TOML.
- [ ] Malformed or unknown configuration values return `INVALID_CONFIG`.
- [ ] Runtime-path creation failures return `RUNTIME_PATH_ERROR`.
- [ ] Runtime and session paths cannot escape the application directory.
- [ ] Paths containing spaces and non-ASCII characters are supported.
- [ ] `.\scripts\quality.ps1` passes.
- [ ] The existing coverage threshold continues to pass.

---

## 2. Ordering and Dependencies

```text
Step 1  ← CORE-001, CORE-002
  │       Replace the bootstrap version literal with importlib.metadata.
  │
Step 2  ← CORE-003
  │       Create the package skeletons.
  │
Step 3  ← ERR-001, ERR-002, ERR-003, ERR-004
  │       Create stable errors before models, config, or paths depend on them.
  │
Step 4  ← MOD-001–MOD-012, MOD-014
  │       Create strict shared models and reject unknown command types.
  │
Step 5  ← PATH-001–PATH-007
  │       Create safe platformdirs-based application paths.
  │
Step 6  ← CFG-001–CFG-009
  │       Add TOML writing dependency and implement configuration load/save.
  │
Step 7  ← ERR-005, MOD-013, PATH-008
          Add complete tests and run the quality suite.
```

Implementation must not proceed to a dependent step while the previous step fails formatting, linting, typing, or its focused tests.

---

## 3. Step-by-Step Implementation

## Step 1 — Package Version Metadata (CORE-001, CORE-002)

### 3.1 Replace `src/agentic_blender/__init__.py`

Replace the Phase 0 bootstrap literal with installed distribution metadata:

```python
"""Agentic Blender — agent-agnostic MCP server and Blender extension."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agentic-blender")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
```

The fallback exists only for direct source-tree execution without installation. Normal development through `uv run` uses the editable installed package and must report `0.1.0`.

### 3.2 Update `tests/test_package.py`

```python
"""Package metadata tests."""

from importlib.metadata import version

import pytest

import agentic_blender


@pytest.mark.unit
def test_package_version_matches_distribution_metadata() -> None:
    """Runtime version matches the installed distribution metadata."""
    assert agentic_blender.__version__ == version("agentic-blender")


@pytest.mark.unit
def test_package_exports_version() -> None:
    """The public package exports one non-empty version string."""
    assert agentic_blender.__all__ == ["__version__"]
    assert isinstance(agentic_blender.__version__, str)
    assert agentic_blender.__version__
```

### 3.3 Verify

```powershell
uv run python -c "import agentic_blender; print(agentic_blender.__version__)"
uv run pytest tests/test_package.py -m unit
```

Expected version:

```text
0.1.0
```

---

## Step 2 — Package Skeletons (CORE-003)

Create the following package structure:

```text
src/agentic_blender/
├── __init__.py
├── models/
│   └── __init__.py
├── ipc/
│   └── __init__.py
├── blender/
│   └── __init__.py
├── tools/
│   └── __init__.py
├── capture/
│   └── __init__.py
├── platform/
│   ├── __init__.py
│   └── windows/
│       └── __init__.py
├── mcp_adapter/
│   └── __init__.py
└── resources/
    └── __init__.py
```

This is:

- Eight top-level sub-packages:
  - `models`
  - `ipc`
  - `blender`
  - `tools`
  - `capture`
  - `platform`
  - `mcp_adapter`
  - `resources`
- One nested platform package:
  - `platform/windows`

Each skeleton `__init__.py` must contain only its module docstring.

Suggested contents:

```python
# models/__init__.py
"""Shared models for configuration, IPC, sessions, scenes, and tool results."""
```

```python
# ipc/__init__.py
"""File-based IPC client and session coordination."""
```

```python
# blender/__init__.py
"""Blender discovery, compatibility, process, and launch services."""
```

```python
# tools/__init__.py
"""User-facing Agentic Blender tool implementations."""
```

```python
# capture/__init__.py
"""Blender window screenshot capture services."""
```

```python
# platform/__init__.py
"""Platform-specific integration services."""
```

```python
# platform/windows/__init__.py
"""Windows-specific process, window, and filesystem integration."""
```

```python
# mcp_adapter/__init__.py
"""MCP server transport, registration, and result adaptation."""
```

```python
# resources/__init__.py
"""Bundled Blender extension and generic agent workflow resources."""
```

Do not import Windows-only modules from `platform/windows/__init__.py` during this phase.

Do not create or import `bpy` modules during this phase.

### Verify

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src/agentic_blender/
```

---

## Step 3 — Error System (ERR-001–ERR-004)

## 3.1 File Layout

```text
src/agentic_blender/models/
├── __init__.py
├── base.py
└── errors.py
```

## 3.2 `models/base.py`

Create one shared base model for public serialized models:

```python
"""Shared configuration for serialized Pydantic models."""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


def utc_now() -> datetime.datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


class FrozenModel(BaseModel):
    """Base for validated models with attribute-level immutability."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
    )
```

`frozen=True` prevents normal field reassignment. It does not guarantee deep immutability or hashability when a model contains dictionaries or other unhashable values.

## 3.3 `models/errors.py`

```python
"""Stable application errors shared by CLI, MCP, IPC, and internal services."""

from __future__ import annotations

import enum
from collections.abc import Mapping
from typing import Final

from pydantic import Field, JsonValue

from agentic_blender.models.base import FrozenModel


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
    ) -> "ErrorDetail":
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
    ) -> "AppError":
        """Preserve AppError or wrap another exception at an application boundary."""
        if isinstance(exc, cls):
            return exc

        merged_context: dict[str, JsonValue] = dict(context or {})
        merged_context.setdefault("exception_type", type(exc).__name__)

        if str(exc):
            merged_context.setdefault("reason", str(exc))

        return cls(fallback_code, context=merged_context)
```

## 3.4 Initial `models/__init__.py`

```python
"""Shared models for configuration, IPC, sessions, scenes, and tool results."""

from agentic_blender.models.errors import AppError, ErrorCode, ErrorDetail

__all__ = [
    "AppError",
    "ErrorCode",
    "ErrorDetail",
]
```

### Error-System Requirements

- Every `ErrorCode` must have exactly one canonical message/action entry.
- `AppError.to_dict()` must return enum values as strings, not enum objects.
- Generic exceptions are converted only at application boundaries using `AppError.from_exception()`.
- Context must contain JSON-compatible values only.
- Exception conversion must preserve an existing `AppError`.
- Error messages must not refer to nonexistent commands such as `agentic-blender connect` or nonexistent tools such as `get_scene_summary`.

---

## Step 4 — Shared Models (MOD-001–MOD-012, MOD-014)

## 4.1 File Layout

```text
src/agentic_blender/models/
├── __init__.py
├── base.py
├── errors.py
├── geometry.py
├── blender_version.py
├── process.py
├── session.py
├── heartbeat.py
├── workflow.py
├── ipc.py
├── scene.py
├── screenshot.py
└── export.py
```

## 4.2 `geometry.py` (MOD-001)

```python
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
    scale: Vector3 = Field(
        default_factory=lambda: Vector3(x=1.0, y=1.0, z=1.0)
    )
```

`allow_inf_nan=False` is inherited from `FrozenModel`, so NaN and infinite coordinates are rejected.

## 4.3 `blender_version.py` (MOD-002)

```python
"""Blender version and support-state models."""

from __future__ import annotations

import enum
from typing import Final

from pydantic import NonNegativeInt, model_validator

from agentic_blender.models.base import FrozenModel


class BlenderSupportState(str, enum.Enum):
    """Support classification for a detected Blender version."""

    SUPPORTED = "SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    UNSUPPORTED = "UNSUPPORTED"


_SUPPORTED_VERSIONS: Final[frozenset[tuple[int, int, int]]] = frozenset(
    {(5, 2, 0)}
)
_MINIMUM_VERSION: Final[tuple[int, int, int]] = (5, 2, 0)


def classify_blender_version(
    major: int,
    minor: int,
    patch: int,
) -> BlenderSupportState:
    """Classify a Blender version against the approved v0.1.0 matrix."""
    version_tuple = (major, minor, patch)

    if version_tuple in _SUPPORTED_VERSIONS:
        return BlenderSupportState.SUPPORTED

    if version_tuple > _MINIMUM_VERSION:
        return BlenderSupportState.UNVERIFIED

    return BlenderSupportState.UNSUPPORTED


class BlenderVersion(FrozenModel):
    """Parsed Blender version and its validated support classification."""

    major: NonNegativeInt
    minor: NonNegativeInt
    patch: NonNegativeInt
    support_state: BlenderSupportState

    @property
    def version_string(self) -> str:
        """Return a dotted version string."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def classify(
        cls,
        major: int,
        minor: int,
        patch: int,
    ) -> "BlenderVersion":
        """Create a classified BlenderVersion."""
        return cls(
            major=major,
            minor=minor,
            patch=patch,
            support_state=classify_blender_version(major, minor, patch),
        )

    @model_validator(mode="after")
    def _support_state_matches_version(self) -> "BlenderVersion":
        expected = classify_blender_version(self.major, self.minor, self.patch)

        if self.support_state is not expected:
            raise ValueError(
                "support_state does not match the Blender version classification"
            )

        return self
```

Important version policy:

- `5.2.0` is `SUPPORTED`.
- Later `5.2.x`, `5.3+`, or later major versions are `UNVERIFIED` until explicitly approved.
- Versions older than `5.2.0` are `UNSUPPORTED`.
- Do not automatically mark every `5.2.x` patch release supported.

## 4.4 `process.py` (MOD-003)

```python
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
```

Do not add `pywin32` calls to this model module. Process and window discovery are Phase 2 behaviors.

## 4.5 `session.py` (MOD-004)

```python
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
```

Raw session authentication secrets are not part of long-lived configuration. The exact authenticated session-file format is finalized in Phase 3.

## 4.6 `heartbeat.py` (MOD-005)

```python
"""Heartbeat payload published by the Blender extension."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import AwareDatetime, Field, PositiveInt, StringConstraints
from typing_extensions import Annotated

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
```

The extension sends the raw dotted Blender version. The external process classifies it using `BlenderVersion`.

## 4.7 `workflow.py` (MOD-006)

```python
"""Agent workflow status models displayed by the Blender extension."""

from __future__ import annotations

import enum

from pydantic import AwareDatetime, Field, NonNegativeInt, PositiveInt, model_validator

from agentic_blender.models.base import FrozenModel, utc_now


class WorkflowState(str, enum.Enum):
    """Public and internal workflow states for v0.1.0."""

    IDLE = "IDLE"
    BLENDER_STARTING = "BLENDER_STARTING"
    READY = "READY"
    PLANNING = "PLANNING"
    PLAN_REVIEW = "PLAN_REVIEW"
    IMPLEMENTING = "IMPLEMENTING"
    VERIFYING_STATE = "VERIFYING_STATE"
    CAPTURING_SCREENSHOT = "CAPTURING_SCREENSHOT"
    VISUAL_REVIEW = "VISUAL_REVIEW"
    FIXING = "FIXING"
    EXPORTING = "EXPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DISCONNECTED = "DISCONNECTED"


class WorkflowStatus(FrozenModel):
    """Snapshot consumed by the Blender workflow-status UI."""

    state: WorkflowState
    task_summary: str | None = Field(default=None, max_length=500)
    current_step: str | None = Field(default=None, max_length=500)
    attempt: NonNegativeInt = 0
    max_attempts: PositiveInt = 3
    last_action: str | None = Field(default=None, max_length=500)
    failure_reason: str | None = Field(default=None, max_length=2000)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _attempt_is_within_limit(self) -> "WorkflowStatus":
        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot be greater than max_attempts")

        if self.state is WorkflowState.FAILED and not self.failure_reason:
            raise ValueError("failure_reason is required when state is FAILED")

        return self
```

The state names must match the PRD. Do not replace `COMPLETED` with `DONE`, `VERIFYING_STATE` with `VERIFYING`, or omit review and screenshot phases.

## 4.8 `ipc.py` (MOD-007, MOD-008, MOD-014)

```python
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
    def _status_matches_error(self) -> "ResponseEnvelope":
        if self.status is ResponseStatus.ERROR and self.error is None:
            raise ValueError("error is required when status is ERROR")

        if self.status is ResponseStatus.OK and self.error is not None:
            raise ValueError("error must be omitted when status is OK")

        return self
```

Notes:

- Screenshot capture is external OS-level behavior, so there is no `TAKE_SCREENSHOT` Blender-extension command.
- The public MCP tool may be named `export`, while the internal Blender command is `SAVE_BLEND`.
- `MOD-014` is satisfied because `CommandType` rejects unknown command strings.
- `JsonValue` prevents arbitrary Python objects from entering payloads.
- Typed command payload models may be added beside these envelopes when Phase 3 finalizes the IPC protocol.

## 4.9 `scene.py` (MOD-010)

```python
"""Machine-verifiable Blender scene and object summaries."""

from __future__ import annotations

from pathlib import Path

from pydantic import NonNegativeInt, model_validator

from agentic_blender.models.base import FrozenModel
from agentic_blender.models.blender_version import BlenderVersion
from agentic_blender.models.geometry import Transform, Vector3


class ObjectSummary(FrozenModel):
    """Compact representation of one Blender object."""

    name: str
    object_type: str
    transform: Transform
    dimensions: Vector3 | None = None


class SceneSummary(FrozenModel):
    """Programmatic verification snapshot of the active Blender scene."""

    scene_name: str
    objects: tuple[ObjectSummary, ...] = ()
    active_object: str | None = None
    mesh_count: NonNegativeInt
    project_path: Path | None = None
    is_dirty: bool
    blender_version: BlenderVersion

    @property
    def object_count(self) -> int:
        """Return the number of objects in the snapshot."""
        return len(self.objects)

    @model_validator(mode="after")
    def _summary_is_consistent(self) -> "SceneSummary":
        names = {item.name for item in self.objects}

        if self.active_object is not None and self.active_object not in names:
            raise ValueError("active_object must reference an object in objects")

        expected_mesh_count = sum(
            item.object_type == "MESH" for item in self.objects
        )

        if self.mesh_count != expected_mesh_count:
            raise ValueError("mesh_count does not match the object summaries")

        return self
```

This model supports the v0.1.0 acceptance checks:

- `Cube` is absent.
- `Sphere` exists.
- `Sphere` is a mesh.
- `Sphere` has the expected transform.
- The project path and dirty state are known.
- The Blender version is known.

## 4.10 `screenshot.py` (MOD-011)

```python
"""Blender application screenshot result model."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Literal

from pydantic import AwareDatetime, Field, PositiveInt, StringConstraints, field_validator
from typing_extensions import Annotated

from agentic_blender.models.base import FrozenModel, utc_now

Sha256Hex = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{64}$"),
]


class ScreenshotCaptureMode(str, enum.Enum):
    """Supported screenshot capture modes."""

    BLENDER_WINDOW = "BLENDER_WINDOW"


class ScreenshotResult(FrozenModel):
    """Validated PNG artifact produced by screenshot capture."""

    path: Path
    width: PositiveInt
    height: PositiveInt
    file_size_bytes: PositiveInt
    capture_mode: ScreenshotCaptureMode = ScreenshotCaptureMode.BLENDER_WINDOW
    mime_type: Literal["image/png"] = "image/png"
    captured_at: AwareDatetime = Field(default_factory=utc_now)
    sha256: Sha256Hex | None = None

    @field_validator("path")
    @classmethod
    def _path_is_absolute_png(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("screenshot path must be absolute")

        if value.suffix.lower() != ".png":
            raise ValueError("screenshot path must use the .png extension")

        return value
```

## 4.11 `export.py` (MOD-012)

```python
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
```

`verified` reports file-level verification performed by the export service. It does not replace the separate agent visual-review result.

## 4.12 Complete `models/__init__.py`

```python
"""Shared models for configuration, IPC, sessions, scenes, and tool results."""

from agentic_blender.models.blender_version import (
    BlenderSupportState,
    BlenderVersion,
    classify_blender_version,
)
from agentic_blender.models.errors import AppError, ErrorCode, ErrorDetail
from agentic_blender.models.export import ExportResult
from agentic_blender.models.geometry import Transform, Vector3
from agentic_blender.models.heartbeat import HeartbeatPayload
from agentic_blender.models.ipc import (
    CommandEnvelope,
    CommandType,
    ResponseEnvelope,
    ResponseStatus,
)
from agentic_blender.models.process import BlenderProcess, WindowIdentity
from agentic_blender.models.scene import ObjectSummary, SceneSummary
from agentic_blender.models.screenshot import (
    ScreenshotCaptureMode,
    ScreenshotResult,
)
from agentic_blender.models.session import SessionMetadata
from agentic_blender.models.workflow import WorkflowState, WorkflowStatus

__all__ = [
    "AppError",
    "BlenderProcess",
    "BlenderSupportState",
    "BlenderVersion",
    "CommandEnvelope",
    "CommandType",
    "ErrorCode",
    "ErrorDetail",
    "ExportResult",
    "HeartbeatPayload",
    "ObjectSummary",
    "ResponseEnvelope",
    "ResponseStatus",
    "SceneSummary",
    "ScreenshotCaptureMode",
    "ScreenshotResult",
    "SessionMetadata",
    "Transform",
    "Vector3",
    "WindowIdentity",
    "WorkflowState",
    "WorkflowStatus",
    "classify_blender_version",
]
```

---

## Step 5 — Application Paths (PATH-001–PATH-007)

## 5.1 File Layout

```text
src/agentic_blender/
└── _paths.py
```

The module is package-private because callers should use path accessors rather than hard-coded locations.

## 5.2 `src/agentic_blender/_paths.py`

```python
"""Per-user Agentic Blender paths and safe directory preparation."""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

from platformdirs import PlatformDirs

from agentic_blender.models.errors import AppError, ErrorCode

_APP_NAME = "agentic-blender"


def _dirs() -> PlatformDirs:
    """Return flat per-user platform directories."""
    return PlatformDirs(
        appname=_APP_NAME,
        appauthor=False,
        version=None,
        roaming=False,
        opinion=True,
        ensure_exists=False,
    )


def config_dir() -> Path:
    """Return the local user configuration directory."""
    return _dirs().user_config_path


def data_dir() -> Path:
    """Return the local user data directory."""
    return _dirs().user_data_path


def cache_dir() -> Path:
    """Return the local user cache directory."""
    return _dirs().user_cache_path


def log_dir() -> Path:
    """Return the local user log directory."""
    return _dirs().user_log_path


def runtime_dir() -> Path:
    """Return the root containing active session directories."""
    return data_dir() / "runtime"


def session_dir(session_id: uuid.UUID | str) -> Path:
    """Return the canonical runtime directory for one UUID session."""
    try:
        canonical_id = str(uuid.UUID(str(session_id)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise AppError(
            ErrorCode.INVALID_SESSION,
            context={"session_id": str(session_id)},
        ) from exc

    return runtime_dir() / canonical_id


def extension_staging_dir() -> Path:
    """Return the staging directory for the packaged Blender extension."""
    return data_dir() / "extension"


def default_screenshots_dir() -> Path:
    """Return the default screenshot output directory."""
    return data_dir() / "screenshots"


def default_exports_dir() -> Path:
    """Return the default Blender project output directory."""
    return data_dir() / "exports"


def config_file() -> Path:
    """Return the user TOML configuration path."""
    return config_dir() / "config.toml"


def log_file() -> Path:
    """Return the default application log file path."""
    return log_dir() / "agentic-blender.log"


def normalize_path(value: str | Path) -> Path:
    """Expand variables and user markers, then return an absolute path."""
    expanded = os.path.expandvars(str(value))
    return Path(expanded).expanduser().resolve(strict=False)


def required_directories() -> tuple[Path, ...]:
    """Return all directories required by normal local operation."""
    return (
        config_dir(),
        data_dir(),
        cache_dir(),
        log_dir(),
        runtime_dir(),
        extension_staging_dir(),
        default_screenshots_dir(),
        default_exports_dir(),
    )


def _create_directory(path: Path) -> None:
    """Create one directory or raise a structured runtime-path error."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AppError(
            ErrorCode.RUNTIME_PATH_ERROR,
            context={
                "path": str(path),
                "operation": "create_directory",
                "reason": str(exc),
            },
        ) from exc

    if not path.is_dir():
        raise AppError(
            ErrorCode.RUNTIME_PATH_ERROR,
            context={
                "path": str(path),
                "operation": "validate_directory",
                "reason": "Path exists but is not a directory.",
            },
        )


def _verify_writable(path: Path) -> None:
    """Test actual file creation and deletion inside a directory."""
    probe_path: Path | None = None

    try:
        descriptor, raw_probe_path = tempfile.mkstemp(
            prefix=".agentic-blender-write-test-",
            dir=path,
        )
        os.close(descriptor)
        probe_path = Path(raw_probe_path)
        probe_path.unlink()
    except OSError as exc:
        if probe_path is not None:
            probe_path.unlink(missing_ok=True)

        raise AppError(
            ErrorCode.RUNTIME_PATH_ERROR,
            context={
                "path": str(path),
                "operation": "verify_writable",
                "reason": str(exc),
            },
        ) from exc


def ensure_runtime_directories() -> tuple[Path, ...]:
    """Create and verify all required per-user directories."""
    directories = required_directories()

    for directory in directories:
        _create_directory(directory)
        _verify_writable(directory)

    return directories
```

### 5.3 Path Policy

- `appauthor=False` intentionally produces a flat Windows path such as:
  - `%LOCALAPPDATA%\agentic-blender`
- `roaming=False` is intentional because Blender executable paths and runtime sessions are machine-specific.
- `os.access()` is not used as the sole writability check.
- Session directories accept UUID values only.
- A value such as `..\..\escape` must return `INVALID_SESSION`.
- `normalize_path()` supports:
  - `~`
  - environment variables
  - spaces
  - non-ASCII characters
  - relative path components
- User-facing output path validation remains the responsibility of screenshot/export services and uses `INVALID_OUTPUT_PATH`, not `RUNTIME_PATH_ERROR`.

---

## Step 6 — Configuration (CFG-001–CFG-009)

## 6.1 Add TOML Serialization Dependencies

Phase 0 includes TOML reading through `pydantic-settings`, but safe TOML persistence requires an explicit writer.

Run:

```powershell
uv add `
  "tomli-w>=1.2,<2" `
  "tomli>=2,<3; python_version < '3.11'"
```

Commit the updated `pyproject.toml` and `uv.lock` with the configuration implementation.

## 6.2 File Layout

```text
src/agentic_blender/
└── config.py
```

## 6.3 `src/agentic_blender/config.py`

```python
"""Validated Agentic Blender configuration loading and persistence."""

from __future__ import annotations

import enum
import os
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import tomli_w
from pydantic import ConfigDict, Field, ValidationError, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    SettingsError,
    TomlConfigSettingsSource,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from agentic_blender._paths import config_file, normalize_path
from agentic_blender.models.base import FrozenModel
from agentic_blender.models.errors import AppError, ErrorCode


class LogLevel(str, enum.Enum):
    """Supported application log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BlenderConfig(FrozenModel):
    """Configured Blender executable and additional search roots."""

    executable: Path | None = None
    search_paths: tuple[Path, ...] = ()


class TimeoutConfig(FrozenModel):
    """Positive timeout values expressed in seconds."""

    startup_seconds: float = Field(default=30.0, gt=0)
    command_seconds: float = Field(default=60.0, gt=0)
    heartbeat_seconds: float = Field(default=10.0, gt=0)


class ScreenshotConfig(FrozenModel):
    """Screenshot defaults."""

    output_dir: Path | None = None


class ExtensionUIConfig(FrozenModel):
    """Externally configurable Blender extension UI preferences."""

    show_status_panel: bool = True
    show_viewport_banner: bool = True


class AppConfig(BaseSettings):
    """Root application configuration.

    Precedence from highest to lowest:

    1. Values passed directly to the constructor.
    2. AGENTIC_BLENDER_* environment variables.
    3. The per-user config.toml file.
    4. Field defaults.
    """

    blender: BlenderConfig = Field(default_factory=BlenderConfig)
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)
    screenshot: ScreenshotConfig = Field(default_factory=ScreenshotConfig)
    extension_ui: ExtensionUIConfig = Field(default_factory=ExtensionUIConfig)
    log_level: LogLevel = LogLevel.INFO

    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_BLENDER_",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="forbid",
        frozen=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Return constructor, environment, and optional TOML sources."""
        user_config = config_file()

        if not user_config.exists():
            return (
                init_settings,
                env_settings,
            )

        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(
                settings_cls,
                toml_file=user_config,
                deep_merge=True,
            ),
        )

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalise_log_level(cls, value: object) -> object:
        if isinstance(value, str):
            return value.upper()

        return value


def load_config(
    overrides: Mapping[str, object] | None = None,
) -> AppConfig:
    """Load and validate configuration using the documented precedence."""
    try:
        return AppConfig(**dict(overrides or {}))
    except (ValidationError, SettingsError, OSError, ValueError) as exc:
        raise AppError(
            ErrorCode.INVALID_CONFIG,
            context={
                "config_file": str(config_file()),
                "reason": str(exc),
            },
        ) from exc


def _serializable_config(config: AppConfig) -> dict[str, Any]:
    """Return TOML-compatible configuration data without null values."""
    return config.model_dump(
        mode="json",
        exclude_none=True,
    )


def save_config(
    config: AppConfig,
    *,
    destination: str | Path | None = None,
) -> Path:
    """Persist configuration atomically as validated TOML."""
    target = normalize_path(destination or config_file())
    temporary_path: Path | None = None

    try:
        target.parent.mkdir(parents=True, exist_ok=True)

        data = _serializable_config(config)
        rendered = tomli_w.dumps(data)

        # Verify the generated content before replacing the active config.
        tomllib.loads(rendered)

        descriptor, raw_temporary_path = tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
        )
        temporary_path = Path(raw_temporary_path)

        with os.fdopen(
            descriptor,
            mode="w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, target)
        temporary_path = None
        return target

    except (OSError, TypeError, ValueError) as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

        raise AppError(
            ErrorCode.INVALID_CONFIG,
            context={
                "config_file": str(target),
                "operation": "save_config",
                "reason": str(exc),
            },
        ) from exc
```

## 6.4 Configuration Format

A valid `config.toml` may contain:

```toml
log_level = "INFO"

[blender]
executable = "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"
search_paths = [
  "D:\\Applications\\Blender",
]

[timeouts]
startup_seconds = 30.0
command_seconds = 60.0
heartbeat_seconds = 10.0

[screenshot]
output_dir = "D:\\Agentic Blender\\Screenshots"

[extension_ui]
show_status_panel = true
show_viewport_banner = true
```

Equivalent environment variables include:

```text
AGENTIC_BLENDER_LOG_LEVEL=DEBUG
AGENTIC_BLENDER_BLENDER__EXECUTABLE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
AGENTIC_BLENDER_TIMEOUTS__COMMAND_SECONDS=120
AGENTIC_BLENDER_EXTENSION_UI__SHOW_VIEWPORT_BANNER=false
```

## 6.5 Configuration Policy

- Nested configuration classes remain `BaseModel` subclasses through `FrozenModel`.
- Only the root `AppConfig` reads settings sources.
- Unknown TOML keys are rejected.
- Unknown direct constructor keys are rejected.
- Environment variable names are case-insensitive on Windows.
- Empty environment variables are ignored.
- No v0.1.0 configuration field contains authentication tokens or credentials.
- Future secret-bearing values must not be added to `AppConfig` without a separate persistence and redaction design.
- `save_config()` must never partially overwrite a valid configuration file.
- CLI code later passes overrides through `load_config({"field": value})` rather than mutating a loaded frozen model.

---

## Step 7 — Tests (ERR-005, MOD-013, PATH-008)

## 7.1 Test Layout

```text
tests/
├── __init__.py
├── test_package.py
├── models/
│   ├── __init__.py
│   ├── test_blender_version.py
│   ├── test_errors.py
│   ├── test_geometry.py
│   ├── test_ipc.py
│   ├── test_round_trip.py
│   └── test_workflow.py
├── test_config.py
└── test_paths.py
```

Create missing directories and package files:

```powershell
New-Item -ItemType Directory -Path tests\models -Force
New-Item -ItemType File -Path tests\models\__init__.py -Force
```

## 7.2 `tests/models/test_errors.py`

```python
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
```

## 7.3 `tests/models/test_geometry.py`

```python
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
```

## 7.4 `tests/models/test_blender_version.py`

```python
"""Blender version-classification tests."""

import pytest
from pydantic import ValidationError

from agentic_blender.models import (
    BlenderSupportState,
    BlenderVersion,
)


@pytest.mark.unit
def test_blender_520_is_supported() -> None:
    """Blender 5.2.0 LTS is the official supported target."""
    version = BlenderVersion.classify(5, 2, 0)

    assert version.support_state is BlenderSupportState.SUPPORTED
    assert version.version_string == "5.2.0"


@pytest.mark.unit
def test_later_52_patch_is_unverified() -> None:
    """Later 5.2 patch versions require explicit validation."""
    version = BlenderVersion.classify(5, 2, 1)

    assert version.support_state is BlenderSupportState.UNVERIFIED


@pytest.mark.unit
def test_newer_blender_is_unverified() -> None:
    """Newer Blender versions are not advertised as supported."""
    assert (
        BlenderVersion.classify(5, 3, 0).support_state
        is BlenderSupportState.UNVERIFIED
    )


@pytest.mark.unit
def test_older_blender_is_unsupported() -> None:
    """Versions older than 5.2.0 are unsupported."""
    assert (
        BlenderVersion.classify(4, 5, 0).support_state
        is BlenderSupportState.UNSUPPORTED
    )


@pytest.mark.unit
def test_inconsistent_support_state_is_rejected() -> None:
    """Serialized support state cannot contradict the version."""
    with pytest.raises(ValidationError):
        BlenderVersion(
            major=5,
            minor=2,
            patch=0,
            support_state=BlenderSupportState.UNVERIFIED,
        )
```

## 7.5 `tests/models/test_workflow.py`

```python
"""Workflow model tests."""

import pytest
from pydantic import ValidationError

from agentic_blender.models import WorkflowState, WorkflowStatus


@pytest.mark.unit
def test_required_prd_states_exist() -> None:
    """The shared state enum contains every public PRD state."""
    required = {
        "READY",
        "PLANNING",
        "PLAN_REVIEW",
        "IMPLEMENTING",
        "VERIFYING_STATE",
        "CAPTURING_SCREENSHOT",
        "VISUAL_REVIEW",
        "FIXING",
        "EXPORTING",
        "COMPLETED",
        "FAILED",
        "DISCONNECTED",
    }

    assert required <= {state.value for state in WorkflowState}


@pytest.mark.unit
def test_attempt_cannot_exceed_limit() -> None:
    """Bounded workflow loops reject impossible counters."""
    with pytest.raises(ValidationError):
        WorkflowStatus(
            state=WorkflowState.PLAN_REVIEW,
            attempt=4,
            max_attempts=3,
        )


@pytest.mark.unit
def test_failed_state_requires_reason() -> None:
    """A failed workflow cannot omit its failure reason."""
    with pytest.raises(ValidationError):
        WorkflowStatus(state=WorkflowState.FAILED)
```

## 7.6 `tests/models/test_ipc.py`

```python
"""IPC envelope validation tests."""

from pathlib import Path
import uuid

import pytest
from pydantic import ValidationError

from agentic_blender.models import (
    CommandEnvelope,
    CommandType,
    ErrorCode,
    ErrorDetail,
    ResponseEnvelope,
    ResponseStatus,
)


@pytest.mark.unit
@pytest.mark.parametrize("command_type", list(CommandType))
def test_command_type_round_trip(command_type: CommandType) -> None:
    """Every allowlisted command type round-trips through JSON."""
    command = CommandEnvelope(
        command_type=command_type,
        session_id=uuid.uuid4(),
    )

    recovered = CommandEnvelope.model_validate_json(
        command.model_dump_json()
    )

    assert recovered == command


@pytest.mark.unit
def test_unknown_command_type_is_rejected() -> None:
    """Unknown command strings are rejected by model validation."""
    raw = (
        '{"command_type":"EXECUTE_PYTHON",'
        '"session_id":"00000000-0000-0000-0000-000000000001"}'
    )

    with pytest.raises(ValidationError):
        CommandEnvelope.model_validate_json(raw)


@pytest.mark.unit
def test_payload_rejects_non_json_values() -> None:
    """Payloads cannot contain arbitrary Python objects."""
    with pytest.raises(ValidationError):
        CommandEnvelope(
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            payload={"path": Path("not-json")},
        )


@pytest.mark.unit
def test_error_response_requires_error_detail() -> None:
    """ERROR responses require one structured error."""
    with pytest.raises(ValidationError):
        ResponseEnvelope(
            command_id=uuid.uuid4(),
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            status=ResponseStatus.ERROR,
        )


@pytest.mark.unit
def test_ok_response_rejects_error_detail() -> None:
    """OK responses cannot contain an error payload."""
    with pytest.raises(ValidationError):
        ResponseEnvelope(
            command_id=uuid.uuid4(),
            command_type=CommandType.PING,
            session_id=uuid.uuid4(),
            status=ResponseStatus.OK,
            error=ErrorDetail.for_code(ErrorCode.COMMAND_TIMEOUT),
        )
```

## 7.7 `tests/models/test_round_trip.py`

```python
"""JSON round-trip tests for every shared model family."""

from pathlib import Path
import uuid

import pytest

from agentic_blender.models import (
    BlenderProcess,
    BlenderVersion,
    CommandEnvelope,
    CommandType,
    ExportResult,
    HeartbeatPayload,
    ObjectSummary,
    ResponseEnvelope,
    ResponseStatus,
    SceneSummary,
    ScreenshotResult,
    SessionMetadata,
    Transform,
    Vector3,
    WindowIdentity,
    WorkflowState,
    WorkflowStatus,
)


def _scene(tmp_path: Path) -> SceneSummary:
    version = BlenderVersion.classify(5, 2, 0)
    sphere = ObjectSummary(
        name="Sphere",
        object_type="MESH",
        transform=Transform(),
        dimensions=Vector3(x=2.0, y=2.0, z=2.0),
    )

    return SceneSummary(
        scene_name="Scene",
        objects=(sphere,),
        active_object="Sphere",
        mesh_count=1,
        project_path=tmp_path / "scene.blend",
        is_dirty=False,
        blender_version=version,
    )


@pytest.mark.unit
def test_all_shared_models_round_trip(tmp_path: Path) -> None:
    """Representative instance of every shared model family round-trips."""
    version = BlenderVersion.classify(5, 2, 0)
    session_id = uuid.uuid4()
    command_id = uuid.uuid4()
    scene = _scene(tmp_path)

    models = [
        Vector3(x=1.0, y=2.0, z=3.0),
        Transform(),
        version,
        WindowIdentity(hwnd=1, title="Blender"),
        BlenderProcess(
            pid=100,
            executable=(tmp_path / "blender.exe").resolve(),
            version=version,
            window=WindowIdentity(hwnd=1, title="Blender"),
        ),
        SessionMetadata(
            session_id=session_id,
            blender_pid=100,
        ),
        HeartbeatPayload(
            session_id=session_id,
            blender_pid=100,
            blender_version="5.2.0",
        ),
        WorkflowStatus(
            state=WorkflowState.IMPLEMENTING,
            task_summary="Replace the cube with a sphere.",
            current_step="Adding Sphere",
            attempt=1,
            max_attempts=3,
        ),
        CommandEnvelope(
            command_id=command_id,
            command_type=CommandType.INSPECT_SCENE,
            session_id=session_id,
        ),
        ResponseEnvelope(
            command_id=command_id,
            command_type=CommandType.INSPECT_SCENE,
            session_id=session_id,
            status=ResponseStatus.OK,
            payload={"mesh_count": 1},
        ),
        scene.objects[0],
        scene,
        ScreenshotResult(
            path=(tmp_path / "capture.png").resolve(),
            width=1920,
            height=1080,
            file_size_bytes=100,
        ),
        ExportResult(
            path=(tmp_path / "scene.blend").resolve(),
            size_bytes=100,
            blender_version=version,
            scene_summary=scene,
            verified=True,
        ),
    ]

    for model in models:
        recovered = type(model).model_validate_json(model.model_dump_json())
        assert recovered == model
```

## 7.8 `tests/test_paths.py`

```python
"""Application-path and runtime-directory tests."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import pytest

import agentic_blender._paths as paths
from agentic_blender.models import AppError, ErrorCode


@pytest.mark.unit
def test_application_roots_are_absolute() -> None:
    """Platform directory accessors return absolute paths."""
    assert paths.config_dir().is_absolute()
    assert paths.data_dir().is_absolute()
    assert paths.cache_dir().is_absolute()
    assert paths.log_dir().is_absolute()


@pytest.mark.unit
def test_normalize_path_expands_user_and_components(tmp_path: Path) -> None:
    """Path normalization resolves parent components."""
    value = tmp_path / "folder" / ".." / "result"
    assert paths.normalize_path(value) == (tmp_path / "result").resolve()


@pytest.mark.unit
def test_normalize_path_handles_spaces_and_unicode(tmp_path: Path) -> None:
    """Spaces and non-ASCII path components are preserved."""
    value = tmp_path / "مشروع Blender" / "ملف.blend"
    normalized = paths.normalize_path(value)

    assert "مشروع Blender" in str(normalized)
    assert normalized.is_absolute()


@pytest.mark.unit
def test_session_dir_uses_canonical_uuid() -> None:
    """Valid session UUIDs remain below the runtime root."""
    session_id = uuid.uuid4()
    result = paths.session_dir(str(session_id))

    assert result.parent == paths.runtime_dir()
    assert result.name == str(session_id)


@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_session",
    ["", "..", "../../escape", "not-a-uuid"],
)
def test_session_dir_rejects_invalid_values(invalid_session: str) -> None:
    """Malformed identifiers cannot escape the runtime root."""
    with pytest.raises(AppError) as caught:
        paths.session_dir(invalid_session)

    assert caught.value.code is ErrorCode.INVALID_SESSION


@pytest.mark.integration
def test_ensure_runtime_directories_creates_all_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All required directories are created and verified."""
    monkeypatch.setattr(paths, "config_dir", lambda: tmp_path / "config")
    monkeypatch.setattr(paths, "data_dir", lambda: tmp_path / "data")
    monkeypatch.setattr(paths, "cache_dir", lambda: tmp_path / "cache")
    monkeypatch.setattr(paths, "log_dir", lambda: tmp_path / "logs")

    created = paths.ensure_runtime_directories()

    assert all(path.is_dir() for path in created)
    assert (tmp_path / "data" / "runtime").is_dir()
    assert (tmp_path / "data" / "extension").is_dir()
    assert (tmp_path / "data" / "screenshots").is_dir()
    assert (tmp_path / "data" / "exports").is_dir()


@pytest.mark.unit
def test_writability_failure_becomes_structured_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Probe failures return RUNTIME_PATH_ERROR."""
    target = tmp_path / "runtime"
    target.mkdir()

    def fail_mkstemp(*args: object, **kwargs: object) -> tuple[int, str]:
        raise PermissionError("denied")

    monkeypatch.setattr(tempfile, "mkstemp", fail_mkstemp)

    with pytest.raises(AppError) as caught:
        paths._verify_writable(target)

    assert caught.value.code is ErrorCode.RUNTIME_PATH_ERROR
```

Accessing `_verify_writable()` directly is acceptable in this focused internal-unit test.

## 7.9 `tests/test_config.py`

```python
"""Configuration precedence, validation, and persistence tests."""

from pathlib import Path

import pytest

import agentic_blender.config as config_module
from agentic_blender.config import (
    AppConfig,
    BlenderConfig,
    TimeoutConfig,
    load_config,
    save_config,
)
from agentic_blender.models import AppError, ErrorCode


@pytest.mark.unit
def test_default_config_is_valid() -> None:
    """Default settings load without filesystem configuration."""
    config = AppConfig()

    assert config.log_level.value == "INFO"
    assert config.timeouts.command_seconds == 60.0


@pytest.mark.integration
def test_toml_configuration_loads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Values load from the user TOML file."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "[timeouts]\ncommand_seconds = 90.0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config_module,
        "config_file",
        lambda: config_path,
    )

    loaded = load_config()

    assert loaded.timeouts.command_seconds == 90.0


@pytest.mark.integration
def test_environment_overrides_toml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Environment variables have higher priority than TOML."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "[timeouts]\ncommand_seconds = 90.0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config_module, "config_file", lambda: config_path)
    monkeypatch.setenv(
        "AGENTIC_BLENDER_TIMEOUTS__COMMAND_SECONDS",
        "120",
    )

    loaded = load_config()

    assert loaded.timeouts.command_seconds == 120.0


@pytest.mark.integration
def test_constructor_override_has_highest_priority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct values supplied by CLI code override environment and TOML."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "[timeouts]\ncommand_seconds = 90.0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config_module, "config_file", lambda: config_path)
    monkeypatch.setenv(
        "AGENTIC_BLENDER_TIMEOUTS__COMMAND_SECONDS",
        "120",
    )

    loaded = load_config(
        {
            "timeouts": {
                "command_seconds": 150.0,
            }
        }
    )

    assert loaded.timeouts.command_seconds == 150.0


@pytest.mark.integration
def test_config_save_and_reload_round_trip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Saved TOML reloads to an equivalent configuration."""
    config_path = tmp_path / "config.toml"
    monkeypatch.setattr(config_module, "config_file", lambda: config_path)

    original = AppConfig(
        blender=BlenderConfig(
            executable=Path("C:/Blender/blender.exe"),
            search_paths=(Path("D:/Blender"),),
        ),
        timeouts=TimeoutConfig(command_seconds=75.0),
    )

    saved_path = save_config(original)
    recovered = load_config()

    assert saved_path == config_path.resolve()
    assert recovered == original


@pytest.mark.integration
def test_malformed_toml_returns_invalid_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed configuration becomes one structured AppError."""
    config_path = tmp_path / "config.toml"
    config_path.write_text("[timeouts\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "config_file", lambda: config_path)

    with pytest.raises(AppError) as caught:
        load_config()

    assert caught.value.code is ErrorCode.INVALID_CONFIG


@pytest.mark.integration
def test_unknown_toml_key_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configuration typos are not silently ignored."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "unknown_setting = true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "config_file", lambda: config_path)

    with pytest.raises(AppError) as caught:
        load_config()

    assert caught.value.code is ErrorCode.INVALID_CONFIG
```

### 7.10 Test Completeness

The tests must verify:

- Every `ErrorCode` has canonical details.
- Errors serialize with string code values.
- Generic exceptions can be converted at boundaries.
- Every shared model family round-trips through JSON.
- NaN and infinity are rejected.
- Unknown model fields are rejected.
- Unknown IPC commands are rejected.
- IPC payloads reject non-JSON values.
- UTC-aware datetime fields round-trip.
- Blender support classification follows policy.
- Workflow retry limits are enforced.
- Scene summaries reject inconsistent counts and active-object names.
- Screenshot and export paths reject wrong extensions.
- Session identifiers cannot traverse outside the runtime root.
- Runtime directory creation handles spaces and Unicode.
- Runtime writability failures become `RUNTIME_PATH_ERROR`.
- TOML, environment, and constructor precedence is correct.
- Invalid TOML and unknown keys become `INVALID_CONFIG`.
- Saving configuration is atomic and round-trips.

---

## 4. File Checklist

After implementation, Phase 1 must contain:

| File | Task(s) | Purpose |
|---|---|---|
| `src/agentic_blender/__init__.py` | CORE-001, CORE-002 | Distribution-derived version metadata |
| `src/agentic_blender/models/base.py` | MOD foundation | Shared strict frozen Pydantic configuration |
| `src/agentic_blender/models/errors.py` | ERR-001–ERR-004, MOD-009 | Stable codes, details, and boundary conversion |
| `src/agentic_blender/models/geometry.py` | MOD-001 | Vector and transform models |
| `src/agentic_blender/models/blender_version.py` | MOD-002 | Blender version and support classification |
| `src/agentic_blender/models/process.py` | MOD-003 | Process and window identities |
| `src/agentic_blender/models/session.py` | MOD-004 | Session metadata |
| `src/agentic_blender/models/heartbeat.py` | MOD-005 | Extension heartbeat payload |
| `src/agentic_blender/models/workflow.py` | MOD-006 | PRD-aligned workflow state |
| `src/agentic_blender/models/ipc.py` | MOD-007, MOD-008, MOD-014 | Strict JSON IPC envelopes |
| `src/agentic_blender/models/scene.py` | MOD-010 | Scene and object summaries |
| `src/agentic_blender/models/screenshot.py` | MOD-011 | Screenshot result |
| `src/agentic_blender/models/export.py` | MOD-012 | Saved project result |
| `src/agentic_blender/models/__init__.py` | CORE-003 | Public model exports |
| `src/agentic_blender/_paths.py` | PATH-001–PATH-007 | Application path policy and preparation |
| `src/agentic_blender/config.py` | CFG-001–CFG-009 | Configuration loading and atomic saving |
| Eight top-level sub-package `__init__.py` files | CORE-003 | Package skeletons |
| `src/agentic_blender/platform/windows/__init__.py` | CORE-003 | Nested Windows skeleton |
| `tests/models/test_errors.py` | ERR-005 | Stable error tests |
| `tests/models/test_geometry.py` | MOD-013 | Geometry validation |
| `tests/models/test_blender_version.py` | MOD-013 | Version classification |
| `tests/models/test_workflow.py` | MOD-013 | Workflow validation |
| `tests/models/test_ipc.py` | MOD-013, MOD-014 | IPC validation |
| `tests/models/test_round_trip.py` | MOD-013 | All-model JSON round trips |
| `tests/test_paths.py` | PATH-008 | Paths and directory creation |
| `tests/test_config.py` | CFG-007–CFG-009 | Config precedence and persistence |
| `pyproject.toml` | CFG-007 | TOML read/write dependencies |
| `uv.lock` | CFG-007 | Locked TOML dependencies |

---

## 5. Commit Strategy

Recommended commits:

```text
feat(core): derive package version from distribution metadata
feat(core): add Phase 1 package skeletons
feat(errors): add stable structured application errors
feat(models): add shared session workflow and IPC models
feat(models): add scene screenshot and export result models
feat(paths): add safe platformdirs runtime paths
feat(config): add validated TOML configuration load and save
test: add Phase 1 model config and path coverage
docs: mark verified Phase 1 tasks complete
```

Commit guidance:

- Update `uv.lock` in the same commit that adds `tomli` and `tomli-w`.
- Each code commit should pass focused tests for its files.
- Do not mark tasks complete before the complete Phase 1 quality suite passes.
- Do not mix Phase 2 Blender-discovery implementation into this branch.

---

## 6. Quality Verification

Run:

```powershell
# Synchronize the locked environment.
uv sync --frozen

# Format check.
uv run --frozen ruff format --check .

# Lint check.
uv run --frozen ruff check .

# Strict external-package type check.
uv run --frozen mypy src/agentic_blender/

# Unit and integration tests.
uv run --frozen pytest tests/ -m "unit or integration"

# Pre-commit hooks.
uv run --frozen pre-commit run --all-files

# Unified wrapper.
.\scripts\quality.ps1

# Package build regression check.
uv build
```

All commands must exit with code `0`.

### Coverage

- The existing `--cov-fail-under=70` requirement must pass.
- Target at least 85% coverage for Phase 1 modules.
- Excluded future Blender extension sources do not reduce Phase 1 coverage.
- Do not lower the global threshold to make Phase 1 pass.

---

## 7. Resolved Questions

### Q1 — Dedicated Configuration Error

**Resolution:** Add `INVALID_CONFIG`.

Configuration parsing and validation failures must not reuse `INVALID_OUTPUT_PATH`.

### Q2 — Runtime Path Errors

**Resolution:** Add `RUNTIME_PATH_ERROR`.

Internal application-directory failures are different from invalid user artifact destinations.

### Q3 — Nested Settings Models

**Resolution:** Keep nested configuration sections as `BaseModel` subclasses through `FrozenModel`.

Only `AppConfig` reads environment variables and TOML sources.

### Q4 — Configuration Persistence

**Resolution:** Add `tomli-w` and conditionally add `tomli` for Python 3.10.

`save_config()` writes a temporary file in the destination directory, flushes it, and replaces the target atomically.

### Q5 — Blender Patch Versions

**Resolution:** Automatically support only Blender `5.2.0`.

Later versions are `UNVERIFIED` until smoke-tested and explicitly added to the approved set.

### Q6 — Model Immutability

**Resolution:** Use `frozen=True` for attribute-level immutability, but do not claim deep immutability or universal hashability.

### Q7 — Session Directory Safety

**Resolution:** Require UUID session identifiers.

Arbitrary strings are rejected with `INVALID_SESSION`.

### Q8 — Workflow State Names

**Resolution:** Use the exact PRD state names and include internal `IDLE` and `BLENDER_STARTING` states.

### Q9 — Screenshot IPC Command

**Resolution:** Do not create a Blender-extension `TAKE_SCREENSHOT` command.

Full-window screenshot capture is an external Windows operation.

### Q10 — Resource and Windows Skeletons

**Resolution:** Keep `resources/` and `platform/windows/` implementation-free during Phase 1.

They contain docstrings only until later phases add packaged resources and Windows integrations.

No unresolved question blocks Phase 1 implementation.

---

## 8. Final Definition of Done

Phase 1 is complete when:

1. The package version is derived from installed metadata.
2. Eight top-level sub-packages and the nested Windows package exist.
3. No Phase 1 module imports Blender-embedded APIs.
4. Error codes include all PRD-required codes plus `INVALID_CONFIG` and `RUNTIME_PATH_ERROR`.
5. Every error code has canonical user guidance.
6. Errors serialize to JSON-compatible dictionaries.
7. Boundary conversion preserves existing `AppError` instances.
8. Shared models reject unknown fields.
9. Shared models reject non-finite floats.
10. Shared models round-trip through JSON.
11. IDs use UUID validation.
12. IPC payloads accept JSON values only.
13. Unknown IPC command types are rejected.
14. Workflow states match the PRD.
15. Retry counters cannot exceed configured limits.
16. Scene summaries contain transforms, dimensions, active object, mesh count, project path, dirty state, and Blender version.
17. Screenshot results contain absolute PNG path, dimensions, size, capture mode, and timestamp.
18. Export results contain absolute `.blend` path, size, Blender version, scene summary, and verification status.
19. Blender `5.2.0` is supported, newer versions are unverified, and older versions are unsupported.
20. `platformdirs` uses a flat, non-roaming per-user Windows path.
21. Session paths cannot escape the runtime directory.
22. Directory writability is tested through real temporary-file creation.
23. Configuration precedence is constructor → environment → TOML → defaults.
24. TOML configuration saving is atomic.
25. Unknown and malformed configuration values return `INVALID_CONFIG`.
26. Configuration contains no long-lived secrets.
27. All Phase 1 tests pass.
28. The quality script, pre-commit, coverage threshold, and package build pass.
29. `TASKS.md` is updated only after all exit criteria are verified.
