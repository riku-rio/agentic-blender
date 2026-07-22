"""Validated Agentic Blender configuration loading and persistence."""

from __future__ import annotations

import enum
import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomli_w
from pydantic import Field, ValidationError, field_validator
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
from agentic_blender.models.workflow import DEFAULT_MAX_ATTEMPTS

if TYPE_CHECKING:
    from collections.abc import Mapping


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


class WorkflowConfig(FrozenModel):
    """Workflow retry policy."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS


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
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
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
    overrides: Mapping[str, Any] | None = None,
) -> AppConfig:
    """Load and validate configuration using the documented precedence."""
    try:
        return AppConfig.model_validate(dict(overrides or {}))
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

    except (OSError, ValueError) as exc:
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
