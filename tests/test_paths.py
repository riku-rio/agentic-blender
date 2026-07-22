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
