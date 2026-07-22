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
