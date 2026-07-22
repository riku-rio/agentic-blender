"""Blender application screenshot result model."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, PositiveInt, StringConstraints, field_validator

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
