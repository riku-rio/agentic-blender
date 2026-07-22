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
    assert BlenderVersion.classify(5, 3, 0).support_state is BlenderSupportState.UNVERIFIED


@pytest.mark.unit
def test_older_blender_is_unsupported() -> None:
    """Versions older than 5.2.0 are unsupported."""
    assert BlenderVersion.classify(4, 5, 0).support_state is BlenderSupportState.UNSUPPORTED


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
