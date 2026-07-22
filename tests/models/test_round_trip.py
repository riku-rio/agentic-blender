"""JSON round-trip tests for every shared model family."""

import uuid
from pathlib import Path

import pytest

from agentic_blender.models import (
    BlenderProcess,
    BlenderVersion,
    CommandEnvelope,
    CommandType,
    ExportResult,
    HeartbeatPayload,
    ObjectSummary,
    ResponseEnvelope,
    ResponseStatus,
    SceneSummary,
    ScreenshotResult,
    SessionMetadata,
    Transform,
    Vector3,
    WindowIdentity,
    WorkflowState,
    WorkflowStatus,
)


def _scene(tmp_path: Path) -> SceneSummary:
    version = BlenderVersion.classify(5, 2, 0)
    sphere = ObjectSummary(
        name="Sphere",
        object_type="MESH",
        transform=Transform(),
        dimensions=Vector3(x=2.0, y=2.0, z=2.0),
    )

    return SceneSummary(
        scene_name="Scene",
        objects=(sphere,),
        active_object="Sphere",
        mesh_count=1,
        project_path=tmp_path / "scene.blend",
        is_dirty=False,
        blender_version=version,
    )


@pytest.mark.unit
def test_all_shared_models_round_trip(tmp_path: Path) -> None:
    """Representative instance of every shared model family round-trips."""
    version = BlenderVersion.classify(5, 2, 0)
    session_id = uuid.uuid4()
    command_id = uuid.uuid4()
    scene = _scene(tmp_path)

    models = [
        Vector3(x=1.0, y=2.0, z=3.0),
        Transform(),
        version,
        WindowIdentity(hwnd=1, title="Blender"),
        BlenderProcess(
            pid=100,
            executable=(tmp_path / "blender.exe").resolve(),
            version=version,
            window=WindowIdentity(hwnd=1, title="Blender"),
        ),
        SessionMetadata(
            session_id=session_id,
            blender_pid=100,
        ),
        HeartbeatPayload(
            session_id=session_id,
            blender_pid=100,
            blender_version="5.2.0",
        ),
        WorkflowStatus(
            state=WorkflowState.IMPLEMENTING,
            task_summary="Replace the cube with a sphere.",
            current_step="Adding Sphere",
            attempt=1,
            max_attempts=3,
        ),
        CommandEnvelope(
            command_id=command_id,
            command_type=CommandType.INSPECT_SCENE,
            session_id=session_id,
        ),
        ResponseEnvelope(
            command_id=command_id,
            command_type=CommandType.INSPECT_SCENE,
            session_id=session_id,
            status=ResponseStatus.OK,
            payload={"mesh_count": 1},
        ),
        scene.objects[0],
        scene,
        ScreenshotResult(
            path=(tmp_path / "capture.png").resolve(),
            width=1920,
            height=1080,
            file_size_bytes=100,
        ),
        ExportResult(
            path=(tmp_path / "scene.blend").resolve(),
            size_bytes=100,
            blender_version=version,
            scene_summary=scene,
            verified=True,
        ),
    ]

    for model in models:
        recovered = type(model).model_validate_json(model.model_dump_json())
        assert recovered == model
