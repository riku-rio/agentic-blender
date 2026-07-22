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
    def _summary_is_consistent(self) -> SceneSummary:
        names = {item.name for item in self.objects}

        if self.active_object is not None and self.active_object not in names:
            raise ValueError("active_object must reference an object in objects")

        expected_mesh_count = sum(item.object_type == "MESH" for item in self.objects)

        if self.mesh_count != expected_mesh_count:
            raise ValueError("mesh_count does not match the object summaries")

        return self
