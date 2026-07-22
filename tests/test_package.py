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
