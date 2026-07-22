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


_SUPPORTED_VERSIONS: Final[frozenset[tuple[int, int, int]]] = frozenset({(5, 2, 0)})
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
    ) -> BlenderVersion:
        """Create a classified BlenderVersion."""
        return cls(
            major=major,
            minor=minor,
            patch=patch,
            support_state=classify_blender_version(major, minor, patch),
        )

    @model_validator(mode="after")
    def _support_state_matches_version(self) -> BlenderVersion:
        expected = classify_blender_version(self.major, self.minor, self.patch)

        if self.support_state is not expected:
            raise ValueError("support_state does not match the Blender version classification")

        return self
