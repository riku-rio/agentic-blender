"""Package bootstrap tests."""

import pytest

import agentic_blender


@pytest.mark.unit
def test_package_version() -> None:
    """Verify that the package exposes the expected initial version."""
    assert agentic_blender.__version__ == "0.1.0"
