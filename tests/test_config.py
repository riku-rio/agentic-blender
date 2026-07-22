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
