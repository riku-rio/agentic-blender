# Phase 2 Implementation Plan — Blender Discovery and Extension Packaging

## Document Status

* **Tasks covered:** BLD-001–BLD-013, PROC-001–PROC-007, EXTSRC-001–EXTSRC-006, EXTINS-001–EXTINS-010
* **Phase:** 2.1 Blender Discovery · 2.2 Running Process Discovery · 2.3 Extension Source · 2.4 Extension Build and Installation
* **Date:** 2026-07-22
* **Source tasks:** [TASKS.md §2.1–2.4](../TASKS.md)
* **Target branch:** `feat/phase-2-blender-discovery`
* **Repository baseline:** `main` after Phase 1 (`4b8609d73a94e2775bcf37f5251c6b8a7a9587e9`)
* **Official environment:** Windows 10/11 x64 · Blender 5.2.0 LTS · Python 3.10+
* **Prerequisite:** Phase 1 is merged and `.\scripts\quality.ps1` passes.

---

## 1. Purpose

Phase 2 establishes the discovery and packaging layer used by initialization, diagnostics, launching, IPC, and the Blender bridge in later phases.

It must provide:

* Deterministic Blender installation discovery on Windows.
* Safe validation and version interrogation of candidate executables.
* Correct use of the Phase 1 Blender version policy.
* Persistence of the selected executable through the existing nested configuration model.
* Running-process discovery based on executable identity, not process name alone.
* Association of Phase 1 `SessionMetadata` registrations with Blender PIDs.
* A valid Blender extension whose archive root contains `__init__.py` and `blender_manifest.toml`.
* Package-resource staging that works for editable installs and built wheels.
* Deterministic extension validation, build, installation, enablement, state verification, upgrade, and removal.
* Tests that never modify a developer's normal Blender profile.
* A PowerShell helper for manual extension validation and build testing.

This phase does **not** implement:

* Blender launch orchestration.
* Session creation or heartbeat freshness policy.
* File IPC command processing.
* Extension timers or bridge command dispatch.
* MCP server registration.
* Screenshot capture.
* User-facing `init` or `doctor` commands.
* Cross-process extension installation locking; `LOCK-003` remains in Phase 3.

---

## 2. Corrections to the Previous Draft

The implementation must account for the repository as it exists after Phase 1.

1. **Reuse the existing configuration schema.**
   `AppConfig` already contains `blender: BlenderConfig`, and `BlenderConfig` already contains `executable` and `search_paths`. Do not add duplicate top-level fields such as `blender_executable` or `blender_custom_search_paths`.

2. **Reuse the existing shared models.**
   `BlenderProcess`, `BlenderVersion`, `BlenderSupportState`, and `SessionMetadata` already exist. Process discovery may add a state wrapper, but it must not replace those shared models with incompatible duplicates.

3. **Use the existing staging path.**
   `_paths.extension_staging_dir()` already defines the application-owned extension staging directory.

4. **Use a real Blender extension entry point.**
   Blender add-on extensions require `__init__.py` at the extension archive root. `__init_extension__.py` is not a supported replacement.

5. **Do not import the Blender extension package externally.**
   The external Python process cannot import a child package whose `__init__.py` imports `bpy`. Resource discovery must anchor at `agentic_blender.resources` and treat the extension directory as data.

6. **Do not use `Path(str(importlib.resources.files(...)))`.**
   A resource may not be represented by a normal filesystem path. Recursively stage the `Traversable` resource tree into an application-owned temporary directory.

7. **Remove legacy extension metadata.**
   An extension manifest replaces `bl_info`. The extension must use relative imports and `__package__` for `AddonPreferences.bl_idname`.

8. **Align permissions with the file-based architecture.**
   The extension does not need a network permission in Phase 2. It will use local session files in Phase 3, so the manifest may declare a narrowly worded `files` permission.

9. **Use valid extension CLI syntax.**
   `install-file` requires a repository identifier. The documented CLI has `install-file --enable`; it does not provide a standalone `extension enable` subcommand.

10. **Do not use `BLENDER_NOT_FOUND` for extension failures.**
    Add one stable `EXTENSION_OPERATION_FAILED` error code and include the operation stage in context.

11. **Do not select ZIPs by newest modification time.**
    Supply `--output-filepath` and verify that exact artifact.

12. **Do not verify installation using unanchored substring checks.**
    Parse a captured Blender 5.2 `extension list` fixture, and use a Blender-side JSON probe for enabled state.

13. **Do not run integration tests against the real user profile.**
    All `@pytest.mark.blender` tests must override Blender user directories with temporary paths.

---

## 3. Design Rules

1. All external Blender subprocesses go through one private command runner.
2. Every subprocess uses:

   * `stdin=subprocess.DEVNULL`
   * captured `stdout` and `stderr`
   * UTF-8 decoding with replacement
   * an explicit timeout
   * `check=False`
   * `CREATE_NO_WINDOW` on Windows
3. Candidate-specific discovery failures are collected as diagnostics; one bad installation must not hide another usable installation.
4. A directly configured executable is validated first and remains the preferred selection when still usable.
5. Unsupported versions are never returned as usable installations.
6. Unverified versions are returned with their existing `UNVERIFIED` support state; no Phase 2 code silently upgrades them to supported.
7. Windows path deduplication is case-insensitive and based on normalized absolute paths.
8. Process identity is established by the resolved executable path.
9. PID reuse is treated as stale registration metadata when the live executable does not match.
10. `psutil.AccessDenied` and `psutil.NoSuchProcess` mean the process metadata cannot be trusted and are classified as stale or absent.
11. A session registration is associated by `SessionMetadata.blender_pid`, not by session ID membership alone.
12. Multiple connected instances are never silently selected.
13. Extension install, upgrade, and removal target only the dedicated Agentic Blender repository and package ID.
14. No code deletes or edits Blender extension directories directly.
15. Extension source contains no third-party runtime dependency.
16. Extension source must pass Ruff; only mypy is excluded for the Blender-only directory.
17. Extension integration tests use isolated Blender user directories.
18. Idempotency means repeated sequential calls are safe. Concurrency safety is deferred to Phase 3 locking.

---

## 4. Phase Exit Criteria

Phase 2 is complete when:

* [ ] Discovery validates configured paths, custom roots, `PATH`, and standard Windows roots.
* [ ] Blender 5.2.0 is `SUPPORTED`.
* [ ] Versions newer than 5.2.0 are `UNVERIFIED`.
* [ ] Versions older than 5.2.0 are rejected with `BLENDER_UNSUPPORTED_VERSION`.
* [ ] Multiple installations are returned deterministically.
* [ ] The existing `config.blender.executable` field persists and reloads correctly.
* [ ] Running processes are matched by executable path.
* [ ] Session registrations are associated by PID.
* [ ] Connected, disconnected, and stale instances are classified deterministically.
* [ ] The extension archive root contains `__init__.py` and `blender_manifest.toml`.
* [ ] The manifest validates without warnings.
* [ ] The extension source is included in a built wheel.
* [ ] The extension can be built to an exact requested ZIP path.
* [ ] The dedicated local extension repository is created idempotently.
* [ ] The extension can be installed, enabled, queried, upgraded, and removed.
* [ ] Repeated install and removal calls are safe.
* [ ] An unrelated test extension remains installed during Agentic Blender lifecycle tests.
* [ ] Blender integration tests use an isolated temporary profile.
* [ ] `.\scripts\quality.ps1` passes.
* [ ] Coverage remains at or above 70%.

---

## 5. Ordered Implementation

```text
Step 0  Supporting integration changes
  |
Step 1  Shared Blender command runner
  |
Step 2  Installation candidate discovery
  |
Step 3  Executable inspection, result aggregation, selection, persistence
  |
Step 4  Running-process discovery and registration association
  |
Step 5  Blender extension source and package resources
  |
Step 6  Extension staging, validation, and deterministic build
  |
Step 7  Repository management, install, enable, query, upgrade, removal
  |
Step 8  PowerShell helper, integration matrix, quality gate
```

A dependent step must not begin while the previous step fails its focused tests.

---

# Step 0 — Supporting Integration Changes

## 6.1 Files

```text
src/agentic_blender/models/errors.py
tests/models/test_errors.py
pyproject.toml
```

## 6.2 Add a Stable Extension Error

Add:

```python
class ErrorCode(str, enum.Enum):
    # existing values...
    EXTENSION_OPERATION_FAILED = "EXTENSION_OPERATION_FAILED"
```

Add canonical details:

```python
ErrorCode.EXTENSION_OPERATION_FAILED: (
    "The Agentic Blender extension operation failed.",
    "Check the selected Blender installation, extension repository, and operation diagnostics.",
),
```

Every extension failure includes JSON-compatible context:

```text
operation
executable
arguments
returncode
stdout
stderr
repository_id
package_id
artifact
```

Only fields relevant to the failure are included. Output is truncated to a documented maximum, such as 2,000 characters per stream.

## 6.3 Project Configuration

No dependency changes are required.

`psutil`, `types-psutil`, `tomli`, and `tomli-w` already exist.

Do not add `packaging` merely to compare the current package version. Exact version equality is sufficient for Phase 2; a different installed version is treated as an upgrade candidate and verified by Blender.

Keep the existing mypy exclusion:

```toml
[tool.mypy]
exclude = [
  "^src/agentic_blender/resources/blender_extension/",
]
```

Update the old `resources/extension` path if it already appears in configuration.

Do not exclude the extension from Ruff.

---

# Step 1 — Shared Blender Command Runner

## 7.1 File Layout

```text
src/agentic_blender/blender/
+-- __init__.py
+-- _command.py
```

## 7.2 Command Result

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlenderCommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
```

## 7.3 Runner Interface

```python
def run_blender_command(
    executable: Path,
    arguments: Sequence[str],
    *,
    timeout_seconds: float,
    operation: str,
    error_code: ErrorCode,
    environment: Mapping[str, str] | None = None,
    require_success: bool = True,
) -> BlenderCommandResult:
    """Run one non-interactive Blender command with bounded execution."""
```

Required behavior:

1. Normalize the executable path with `_paths.normalize_path`.
2. Build an argument list; never invoke a shell.
3. Pass `stdin=subprocess.DEVNULL`.
4. Pass `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE`.
5. Pass `encoding="utf-8"` and `errors="replace"`.
6. Use `subprocess.CREATE_NO_WINDOW` only when `sys.platform == "win32"`.
7. Merge `environment` over `os.environ` when supplied.
8. Convert `TimeoutExpired` and `OSError` to the supplied stable error code.
9. Convert non-zero return codes when `require_success=True`.
10. Never include secrets or complete environment variables in error context.

This runner is private. Public modules expose domain-specific functions.

## 7.4 Tests

Create `tests/blender/test_command.py`.

Required unit tests:

* successful command returns captured output
* non-zero exit raises the supplied code
* timeout raises the supplied code
* `OSError` raises the supplied code
* `stdin` is `DEVNULL`
* output is captured
* timeout is forwarded
* Windows creation flags are applied only on Windows
* environment overrides merge without mutating `os.environ`
* failure output is truncated

---

# Step 2 — Blender Installation Candidate Discovery

## 8.1 File Layout

```text
src/agentic_blender/blender/
+-- discovery.py
```

## 8.2 Public Models

```python
class BlenderInstallSource(str, enum.Enum):
    CONFIGURED = "CONFIGURED"
    CUSTOM_PATH = "CUSTOM_PATH"
    PATH = "PATH"
    STANDARD = "STANDARD"


class BlenderInstall(FrozenModel):
    executable: Path
    version: BlenderVersion
    source: BlenderInstallSource

    @field_validator("executable")
    @classmethod
    def _normalize_executable(cls, value: Path) -> Path:
        return normalize_path(value)


class BlenderDiscoveryIssue(FrozenModel):
    candidate: Path
    error: ErrorDetail


class BlenderDiscoveryResult(FrozenModel):
    installs: tuple[BlenderInstall, ...] = ()
    issues: tuple[BlenderDiscoveryIssue, ...] = ()
```

`BlenderInstall` is the validated installation record. It does not replace the existing running `BlenderProcess` model.

## 8.3 Candidate Sources

Candidate order is:

1. `BlenderConfig.executable`
2. Each `BlenderConfig.search_paths` entry
3. `shutil.which("blender.exe")`
4. Standard Windows roots

Standard roots are derived from environment variables, not a hard-coded drive:

```python
def _standard_install_roots(environment: Mapping[str, str]) -> tuple[Path, ...]:
    roots: list[Path] = []

    if program_files := environment.get("ProgramFiles"):
        roots.append(Path(program_files) / "Blender Foundation")

    if program_files_x86 := environment.get("ProgramFiles(x86)"):
        roots.append(Path(program_files_x86) / "Blender Foundation")

    if local_app_data := environment.get("LOCALAPPDATA"):
        roots.append(Path(local_app_data) / "Programs" / "Blender Foundation")

    return tuple(roots)
```

Do not scan `WindowsApps`; access is restricted and Microsoft Store installs must be supplied through `PATH` or explicit configuration.

## 8.4 Custom Path Expansion

Each configured search entry may be:

* a direct `blender.exe` file
* a directory containing `blender.exe`
* a Blender Foundation-style root containing child installation directories

Directory expansion is bounded:

```text
<root>\blender.exe
<root>\Blender *\blender.exe
<root>\*\blender.exe
```

Do not perform unbounded recursive filesystem traversal.

Permission failures and missing roots create no exception at collection time.

## 8.5 Deduplication

Deduplicate with a Windows-safe key:

```python
def _path_key(path: Path) -> str:
    normalized = normalize_path(path)
    return os.path.normcase(str(normalized))
```

The first source wins, preserving configured-path priority.

## 8.6 Executable Validation

```python
def _validate_executable(path: Path) -> bool:
    """Return whether the candidate is a non-empty regular blender.exe file."""
```

Required checks:

* file exists
* regular file
* case-insensitive filename is `blender.exe`
* size is greater than zero

Catch `OSError` and return `False`.

Do not attempt to execute a candidate that fails this check.

## 8.7 Tests

Candidate collection tests cover:

* configured executable first
* custom direct executable
* custom installation directory
* custom root containing multiple installs
* `PATH` candidate
* `ProgramFiles`
* `ProgramFiles(x86)`
* per-user `LOCALAPPDATA` root
* missing roots
* access-denied root
* bounded traversal
* case-insensitive deduplication
* duplicate candidate preserves first source

No test launches Blender.

---

# Step 3 — Executable Inspection, Discovery Results, Selection, and Persistence

## 9.1 Version Interrogation

```python
_VERSION_TIMEOUT_SECONDS = 15.0


def _read_blender_version(executable: Path) -> BlenderVersion:
    result = run_blender_command(
        executable,
        ["--version"],
        timeout_seconds=_VERSION_TIMEOUT_SECONDS,
        operation="read_version",
        error_code=ErrorCode.BLENDER_NOT_FOUND,
    )
    return _parse_blender_version(f"{result.stdout}\n{result.stderr}")
```

Parsing both streams avoids depending on one stream for all Blender builds.

## 9.2 Version Parser

```python
_VERSION_PATTERN = re.compile(
    r"(?mi)^\s*Blender\s+"
    r"(?P<major>\d+)\."
    r"(?P<minor>\d+)\."
    r"(?P<patch>\d+)"
    r"(?:\b|[-+])"
)
```

The parser:

* accepts additional build metadata after the patch
* uses the existing `BlenderVersion.classify`
* raises `BLENDER_NOT_FOUND` for malformed output
* includes a bounded output sample in context

## 9.3 Candidate Inspection

```python
def inspect_blender_executable(
    candidate: Path,
    *,
    source: BlenderInstallSource,
) -> BlenderInstall:
    """Validate, interrogate, classify, and return one installation."""
```

Behavior:

* invalid file → `BLENDER_NOT_FOUND`
* unparseable or failed version command → `BLENDER_NOT_FOUND`
* `UNSUPPORTED` version → `BLENDER_UNSUPPORTED_VERSION`
* `SUPPORTED` or `UNVERIFIED` → return `BlenderInstall`

Unsupported error context includes:

```text
executable
detected_version
minimum_version = 5.2.0
```

## 9.4 Discovery Entry Point

```python
def discover_blender_installs(
    config: BlenderConfig,
    *,
    environment: Mapping[str, str] | None = None,
) -> BlenderDiscoveryResult:
    """Inspect every candidate and return usable installs plus diagnostics."""
```

Candidate-specific `AppError` instances are converted to `BlenderDiscoveryIssue`. Discovery does not stop after one failure.

Unexpected programmer errors are not swallowed.

## 9.5 Ordering

Usable installations are ordered by:

1. `SUPPORTED` before `UNVERIFIED`
2. semantic version descending
3. source priority:

   * configured
   * custom path
   * `PATH`
   * standard
4. normalized path ascending

Because configured selection has separate semantics, ordering alone does not override an existing selected executable.

## 9.6 Preferred Selection

```python
def select_preferred_install(
    result: BlenderDiscoveryResult,
    *,
    configured_executable: Path | None,
) -> BlenderInstall | None:
    """Return the configured usable install, otherwise the best usable install."""
```

Rules:

1. If `configured_executable` matches a returned installation, return it.
2. Otherwise return the first `SUPPORTED` installation.
3. Otherwise return the first `UNVERIFIED` installation.
4. Otherwise return `None`.

This helper recommends. It does not persist.

A future CLI must ask the user when multiple viable installations exist.

## 9.7 Persistence

Use the existing nested models:

```python
def persist_selected_install(
    config: AppConfig,
    install: BlenderInstall,
    *,
    destination: str | Path | None = None,
) -> AppConfig:
    updated_blender = config.blender.model_copy(
        update={"executable": install.executable},
    )
    updated_config = config.model_copy(
        update={"blender": updated_blender},
    )
    save_config(updated_config, destination=destination)
    return updated_config
```

Do not modify `config.blender.search_paths`.

The optional destination exists for tests and explicit callers. Production callers normally omit it.

## 9.8 Tests

Create `tests/blender/test_discovery.py`.

Required tests:

* validates `blender.exe`
* rejects wrong filename
* rejects zero-byte file
* parses 5.2.0
* parses version with build suffix
* parses from stderr
* rejects garbage output
* 5.2.0 is supported
* 5.2.1 is unverified
* 5.3.0 is unverified
* 6.0.0 is unverified
* 5.1.x is unsupported
* discovery continues after invalid candidate
* discovery records unsupported diagnostics
* discovery returns empty result when nothing exists
* sort order is deterministic
* configured usable executable remains preferred
* missing configured executable falls back
* nested config persistence round-trips
* persistence preserves search paths
* persistence can target a temporary config file

---

# Step 4 — Running Process Discovery and Session Registration Association

## 10.1 File Layout

```text
src/agentic_blender/blender/
+-- process.py
```

## 10.2 State Model

```python
class BlenderInstanceState(str, enum.Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    STALE = "STALE"


class BlenderInstance(FrozenModel):
    pid: PositiveInt
    install: BlenderInstall
    process: BlenderProcess | None = None
    state: BlenderInstanceState
    session: SessionMetadata | None = None
```

Model invariants:

* `CONNECTED` requires both `process` and `session`.
* `DISCONNECTED` requires `process` and no session.
* `STALE` requires `session`; `process` is absent because the registered identity is no longer trusted.

Use a model validator to enforce these combinations.

## 10.3 Live Process Discovery

```python
def _iter_matching_processes(
    install: BlenderInstall,
) -> dict[int, BlenderProcess]:
    """Return live processes whose executable matches the installation."""
```

Use:

```python
psutil.process_iter(["pid", "name", "exe", "status"])
```

Behavior:

1. Process name is an optional fast rejection only.
2. Exact identity uses normalized executable path equality.
3. Missing executable metadata cannot establish identity and is skipped.
4. Zombies are not returned as live processes.
5. `NoSuchProcess` and `AccessDenied` are skipped.
6. The returned `BlenderProcess` uses:

   * PID from psutil
   * normalized executable
   * version from the selected `BlenderInstall`
   * `window=None` until the Windows window-discovery phase

## 10.4 Stale Registration Detection

```python
def registration_is_stale(
    registration: SessionMetadata,
    install: BlenderInstall,
) -> bool:
    """Return whether a registered PID no longer identifies the selected Blender."""
```

A registration is stale when:

* PID no longer exists
* process cannot be read because of `NoSuchProcess`
* process metadata is inaccessible because of `AccessDenied`
* process is a zombie
* executable path differs from the selected install

This protects against PID reuse.

Heartbeat age is **not** evaluated in Phase 2. Phase 3 session management owns heartbeat freshness.

## 10.5 Discovery Entry Point

```python
def discover_blender_instances(
    install: BlenderInstall,
    *,
    registrations: Sequence[SessionMetadata] = (),
) -> tuple[BlenderInstance, ...]:
    """Merge live processes and session registrations for one installation."""
```

Algorithm:

1. Discover live matching processes keyed by PID.
2. Deduplicate registrations by PID:

   * newest `last_heartbeat_at` wins
   * ties use session UUID lexical order
3. For each winning registration:

   * stale registration → `STALE`
   * matching live PID → `CONNECTED`
4. Remaining live processes without a registration → `DISCONNECTED`
5. Return deterministic order:

   * connected, newest heartbeat first, then PID
   * disconnected, PID ascending
   * stale, PID ascending

## 10.6 Connected Instance Selection

```python
def select_connected_instance(
    instances: Sequence[BlenderInstance],
    *,
    requested_session_id: uuid.UUID | None = None,
) -> BlenderInstance | None:
    """Select only when the result is unambiguous."""
```

Rules:

* requested connected session found → return it
* requested session absent or stale → raise `INVALID_SESSION`
* no connected instances → return `None`
* exactly one connected instance → return it
* multiple connected instances without an explicit session → raise `INVALID_SESSION` with candidate session IDs and PIDs

This is deterministic and does not silently control the wrong Blender process.

## 10.7 Tests

Create `tests/blender/test_process.py`.

Required tests:

* exact executable match
* process name alone is insufficient
* path comparison is case-insensitive on Windows
* no-such-process is skipped
* access-denied process is skipped
* zombie is not live
* dead registered PID is stale
* PID reused by another executable is stale
* valid registered PID is connected
* live unregistered PID is disconnected
* registration association uses `blender_pid`
* duplicate registrations choose newest heartbeat
* connected ordering is deterministic
* stale instances appear last
* explicit session selection works
* ambiguous connected selection raises
* requested stale session raises
* no connected instance returns `None`

All tests mock psutil. No real process is launched.

---

# Step 5 — Blender Extension Source and Package Resources

## 11.1 Directory Layout

```text
src/agentic_blender/resources/
+-- __init__.py
+-- blender_extension/
    +-- __init__.py
    +-- blender_manifest.toml
    +-- preferences.py
```

`blender_extension/__init__.py` is the Blender entry point.

External code must never import `agentic_blender.resources.blender_extension`. It accesses the directory through the parent resource package.

## 11.2 Manifest

Create:

```toml
schema_version = "1.0.0"

id = "agentic_blender"
version = "0.1.0"
name = "Agentic Blender"
tagline = "Connect Blender to local Agentic Blender workflows"
maintainer = "riku-rio <YosefBesn123@gmail.com>"
type = "add-on"

website = "https://github.com/riku-rio/agentic-blender"
blender_version_min = "5.2.0"
platforms = ["windows-x64"]

license = [
  "SPDX:GPL-3.0-or-later",
]

[permissions]
files = "Read and write local Agentic Blender session files"

[build]
paths_exclude_pattern = [
  "__pycache__/",
  ".*",
  "*.zip",
]
```

Manifest rules:

* tagline is at most 64 characters
* tagline has no trailing punctuation
* permission explanation is short and has no trailing punctuation
* no network permission
* no wheels
* no dependency table
* no maximum Blender version
* package ID remains `agentic_blender`
* source and built archive both pass Blender validation without warnings

## 11.3 Extension Entry Point

```python
"""Agentic Blender extension entry point."""

from . import preferences


def register() -> None:
    """Register Agentic Blender extension classes."""
    preferences.register()


def unregister() -> None:
    """Unregister Agentic Blender extension classes."""
    preferences.unregister()
```

Do not add `bl_info`.

All imports inside the extension are relative.

Registration exceptions propagate to Blender.

## 11.4 Preferences

```python
"""Agentic Blender extension preferences."""

import bpy


class AgenticBlenderPreferences(bpy.types.AddonPreferences):
    """User-visible Agentic Blender extension preferences."""

    bl_idname = __package__

    show_status_panel: bpy.props.BoolProperty(
        name="Show Status Panel",
        default=True,
        description="Show Agentic Blender workflow status in the sidebar",
    )

    show_viewport_banner: bpy.props.BoolProperty(
        name="Show Viewport Banner",
        default=True,
        description="Show the active Agentic Blender task in the viewport",
    )

    def draw(self, _context: bpy.types.Context) -> None:
        """Draw extension preferences."""
        layout = self.layout
        layout.prop(self, "show_status_panel")
        layout.prop(self, "show_viewport_banner")


_CLASSES = (AgenticBlenderPreferences,)


def register() -> None:
    """Register preference classes."""
    registered: list[type[bpy.types.Struct]] = []
    try:
        for cls in _CLASSES:
            bpy.utils.register_class(cls)
            registered.append(cls)
    except Exception:
        for cls in reversed(registered):
            bpy.utils.unregister_class(cls)
        raise


def unregister() -> None:
    """Unregister preference classes in reverse order."""
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
```

The property names align with the existing Phase 1 `ExtensionUIConfig`.

Do not add host or port preferences; the architecture is file-based and local.

## 11.5 Version Synchronization

Add `tests/resources/test_extension_manifest.py`.

The test reads:

* `[project].version` from the repository `pyproject.toml`
* `version` from `blender_manifest.toml`

It asserts exact equality.

Also assert:

* manifest ID
* minimum Blender version
* Windows platform
* no network permission
* no wheels
* no dependency table
* tagline constraints
* permission explanation constraints

## 11.6 Wheel Inclusion

The uv build backend includes files under the module root, but Phase 2 must verify the actual distribution.

Add a build integration test or scripted check that:

1. runs `uv build`
2. opens the generated wheel as ZIP
3. asserts these entries exist:

```text
agentic_blender/resources/blender_extension/__init__.py
agentic_blender/resources/blender_extension/preferences.py
agentic_blender/resources/blender_extension/blender_manifest.toml
```

This check may run in CI or pre-release validation; it does not require Blender.

---

# Step 6 — Resource Staging, Validation, and Deterministic Build

## 12.1 File Layout

```text
src/agentic_blender/blender/
+-- extension.py
```

## 12.2 Constants

```python
_RESOURCE_PACKAGE = "agentic_blender.resources"
_RESOURCE_DIRECTORY = "blender_extension"

_EXTENSION_ID = "agentic_blender"
_EXTENSION_REPOSITORY_ID = "agentic_blender_local"
_EXTENSION_REPOSITORY_NAME = "Agentic Blender Local"
_EXTENSION_MODULE = (
    f"bl_ext.{_EXTENSION_REPOSITORY_ID}.{_EXTENSION_ID}"
)

_VALIDATE_TIMEOUT_SECONDS = 30.0
_BUILD_TIMEOUT_SECONDS = 120.0
_INSTALL_TIMEOUT_SECONDS = 120.0
_QUERY_TIMEOUT_SECONDS = 30.0
```

## 12.3 Recursive Resource Staging

```python
def stage_extension_source(destination: Path) -> Path:
    """Copy the bundled resource tree into a real filesystem directory."""
```

Implementation requirements:

1. Anchor with:

   ```python
   root = importlib.resources.files(_RESOURCE_PACKAGE).joinpath(
       _RESOURCE_DIRECTORY,
   )
   ```

2. Verify the resource directory, manifest, and entry point exist.

3. Recursively copy `Traversable` directories and files using:

   * `iterdir()`
   * `is_dir()`
   * `read_bytes()`

4. Write into a newly created destination.

5. Reject path names that escape the destination.

6. Return the staged source directory.

This works for editable installs, normal wheels, and non-filesystem resource loaders.

Do not import the extension child package.

## 12.4 Validation

```python
def validate_extension_source(
    blender_executable: Path,
    source_directory: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Validate a source directory with Blender."""
```

Run:

```text
blender.exe --command extension validate <source_directory>
```

Any non-zero result raises `EXTENSION_OPERATION_FAILED` with `operation="validate_source"`.

After build, validate the archive:

```text
blender.exe --command extension validate <artifact.zip>
```

with `operation="validate_archive"`.

## 12.5 Deterministic Build

```python
def build_extension(
    blender_executable: Path,
    *,
    output_directory: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> Path:
    """Stage, validate, build, validate, and return the exact artifact."""
```

Algorithm:

1. Create `extension_staging_dir()` if needed.

2. Create a unique temporary work directory beneath it.

3. Stage resources into `<work>\source`.

4. Read the manifest version.

5. Choose output directory:

   * caller value when supplied
   * `<work>\dist` otherwise

6. Set the exact output path:

   ```text
   agentic_blender-<version>.zip
   ```

7. Validate staged source.

8. Run:

   ```text
   blender.exe --command extension build
       --source-dir <source>
       --output-filepath <exact-zip>
   ```

9. Assert:

   * exact path exists
   * it is a regular non-empty file
   * no alternate glob selection is used

10. Validate the built archive.

11. When the caller supplied an output directory, retain the artifact.

12. When using a temporary output directory, copy the artifact to a stable path beneath `extension_staging_dir()` before cleaning the work directory.

13. Clean only the unique application-owned work directory.

## 12.6 Unit and Integration Tests

Create `tests/blender/test_extension_resources.py`.

Unit/integration tests without Blender:

* resource root exists
* staging copies all files
* staging never imports `bpy`
* staging works with a fake Traversable tree
* path traversal names are rejected
* exact output filename is derived from manifest version
* command uses `--output-filepath`
* source validation precedes build
* archive validation follows build
* missing artifact raises
* zero-byte artifact raises
* cleanup stays within staging root

Mock subprocesses for command construction.

---

# Step 7 — Repository Management and Extension Lifecycle

## 13.1 Isolated Blender Environment Model

Integration tests need explicit environment overrides.

```python
class BlenderUserEnvironment(FrozenModel):
    user_config: Path
    user_scripts: Path
    user_extensions: Path

    def to_subprocess_environment(self) -> dict[str, str]:
        return {
            "BLENDER_USER_CONFIG": str(self.user_config),
            "BLENDER_USER_SCRIPTS": str(self.user_scripts),
            "BLENDER_USER_EXTENSIONS": str(self.user_extensions),
        }
```

This model may live privately in `extension.py` or in test helpers if production callers do not need it.

Production calls pass `environment=None`.

## 13.2 Dedicated Repository

Use a dedicated local repository:

```text
ID: agentic_blender_local
Name: Agentic Blender Local
Source: USER
```

Do not install into an arbitrary remote repository.

## 13.3 Repository State Probe

Use a small Blender-side Python probe that prints one sentinel-prefixed JSON line.

Example output contract:

```text
AGENTIC_BLENDER_JSON:{"repositories":[{"module":"agentic_blender_local","name":"Agentic Blender Local","source":"USER"}]}
```

The external parser ignores all non-sentinel Blender output.

```python
def query_extension_repositories(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> tuple[ExtensionRepository, ...]:
    """Return normalized user extension repository metadata."""
```

The probe reads the public Blender preferences repository collection.

Do not parse human-oriented `repo-list` output when a JSON probe can provide a stable contract.

## 13.4 Ensure Repository

```python
def ensure_extension_repository(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Create the dedicated repository when absent."""
```

If the repository is absent, run:

```text
blender.exe --command extension repo-add
    --name "Agentic Blender Local"
    --source USER
    agentic_blender_local
```

Then query again and require exactly one matching repository.

If a repository with the same ID has incompatible metadata, fail; do not overwrite or clear repositories.

Never pass `--clear-all`.

## 13.5 Installed Package State

Capture the actual Blender 5.2 output from:

```text
blender.exe --command extension list
```

Store a sanitized fixture:

```text
tests/fixtures/blender_5_2_extension_list.txt
```

Implement a dedicated parser:

```python
class InstalledExtension(FrozenModel):
    repository_id: str
    package_id: str
    version: str


def list_installed_extensions(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> tuple[InstalledExtension, ...]:
    """Return parsed installed packages."""
```

Requirements:

* parser is anchored to complete package/repository fields
* no raw substring test
* malformed relevant lines raise `EXTENSION_OPERATION_FAILED`
* unrelated output is ignored
* a fixture test locks the Blender 5.2 format

## 13.6 Enabled State Probe

Use a Blender-side JSON probe:

```python
def is_extension_enabled(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> bool:
    """Return whether the extension module is enabled in user preferences."""
```

Inside Blender, check:

```python
module_name in bpy.context.preferences.addons
```

where:

```text
bl_ext.agentic_blender_local.agentic_blender
```

The probe prints one sentinel JSON line. External code does not infer enabled state from human-formatted list output.

## 13.7 Enablement

The extension CLI has no standalone `enable` subcommand.

Implement enablement through a bounded Blender-side Python operation:

```python
def enable_extension(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Enable only the Agentic Blender module and persist preferences."""
```

Inside Blender:

1. If already enabled, report success without mutation.

2. Call:

   ```python
   bpy.ops.preferences.addon_enable(module=MODULE_NAME)
   ```

3. Call:

   ```python
   bpy.ops.wm.save_userpref()
   ```

4. Print sentinel JSON with success or an error detail.

5. External code verifies enabled state after the process exits.

Use `--python-exit-code` so an unhandled Blender Python exception produces a non-zero process status.

## 13.8 Installation

```python
def install_extension(
    blender_executable: Path,
    artifact: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Install and enable the artifact in the dedicated repository."""
```

Preconditions:

* artifact exists
* artifact is a non-empty `.zip`
* repository exists

Run:

```text
blender.exe --command extension install-file
    --repo agentic_blender_local
    --enable
    <artifact.zip>
```

Then verify:

* package is installed in the dedicated repository
* installed version equals the artifact manifest version
* extension is enabled

Do not report success until both checks pass.

## 13.9 Extension State

```python
class ExtensionState(FrozenModel):
    repository_id: str
    package_id: str
    installed_version: str | None = None
    enabled: bool = False

    @property
    def installed(self) -> bool:
        return self.installed_version is not None
```

```python
def get_extension_state(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> ExtensionState:
    """Return installed version and enabled state."""
```

## 13.10 Idempotent Ensure/Upgrade

```python
def ensure_extension_installed(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> ExtensionState:
    """Ensure the bundled version is installed and enabled."""
```

Algorithm:

1. Ensure the dedicated repository.
2. Query current state.
3. Read bundled manifest version.
4. If exact version is installed and enabled:

   * return current state
   * do not rebuild or reinstall
5. If exact version is installed but disabled:

   * call `enable_extension`
   * verify and return
6. Otherwise:

   * build the exact bundled artifact
   * call `install_extension`
   * verify and return

Do not remove the previous version before attempting the documented install-file upgrade. A destructive remove-and-reinstall fallback is not allowed because it may discard extension preferences.

If Blender rejects the upgrade, raise `EXTENSION_OPERATION_FAILED` and preserve the existing installation.

## 13.11 Safe Removal

```python
def remove_extension(
    blender_executable: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Remove only the Agentic Blender package."""
```

Behavior:

1. Query state.

2. If absent, return.

3. Run:

   ```text
   blender.exe --command extension remove agentic_blender
   ```

4. Verify the package is absent from the dedicated repository.

5. Leave the dedicated repository in place.

6. Do not remove other packages.

7. Do not remove or rewrite unrelated preferences.

8. A second call is a no-op.

If the Blender 5.2 CLI requires a repository-qualified package identifier, use the exact syntax demonstrated by the checked-in 5.2 command fixture and integration test. Do not guess at runtime.

## 13.12 Public API

Update `src/agentic_blender/blender/__init__.py`:

```python
from agentic_blender.blender.discovery import (
    BlenderDiscoveryIssue,
    BlenderDiscoveryResult,
    BlenderInstall,
    BlenderInstallSource,
    discover_blender_installs,
    inspect_blender_executable,
    persist_selected_install,
    select_preferred_install,
)
from agentic_blender.blender.extension import (
    ExtensionState,
    build_extension,
    enable_extension,
    ensure_extension_installed,
    get_extension_state,
    install_extension,
    remove_extension,
    stage_extension_source,
    validate_extension_source,
)
from agentic_blender.blender.process import (
    BlenderInstance,
    BlenderInstanceState,
    discover_blender_instances,
    registration_is_stale,
    select_connected_instance,
)
```

Export only intentional public functions and models. Keep parsers, probes, command builders, and constants private.

## 13.13 Unit Tests

Create `tests/blender/test_extension.py`.

Mocked tests cover:

* dedicated repository already exists
* dedicated repository is created
* conflicting repository fails without overwrite
* install command includes repository and enable flags
* installation verifies exact version
* enabled probe uses full module name
* exact installed+enabled state is a no-op
* installed+disabled state enables without rebuild
* different version builds and installs
* failed upgrade preserves old state and raises
* absent removal is a no-op
* removal targets only Agentic Blender
* removal verifies absence
* list parser uses fixture
* malformed relevant list output raises
* sentinel JSON parser ignores unrelated Blender logs
* missing sentinel raises
* invalid JSON raises

---

# Step 8 — Blender Integration Tests and PowerShell Helper

## 14.1 Isolated Blender Test Fixture

Create `tests/blender/conftest.py`.

`BLENDER_EXE` enables real-Blender tests.

For each test, create temporary directories and pass:

```text
BLENDER_USER_CONFIG
BLENDER_USER_SCRIPTS
BLENDER_USER_EXTENSIONS
```

The fixture must assert that all three paths are beneath `tmp_path`.

Never inherit the developer's normal Blender profile in automated tests.

## 14.2 Real-Blender Tests

Create `tests/blender/test_extension_blender.py`.

Mark every test:

```python
@pytest.mark.blender
```

Required tests:

1. manifest source validation succeeds
2. built archive validation succeeds
3. exact ZIP artifact exists
4. repository creation is idempotent
5. install succeeds
6. enabled-state probe returns true
7. second ensure call is a no-op
8. disabled extension can be re-enabled
9. upgrade from an older fixture version preserves preferences
10. removal succeeds
11. second removal is a no-op
12. unrelated extension remains installed
13. unrelated repository remains configured

For EXTINS-009, include a minimal dummy extension fixture with a different ID. Build and install it into the isolated profile before exercising Agentic Blender lifecycle operations.

## 14.3 Manual CLI Compatibility Capture

Before merging against Blender 5.2.0 LTS, capture and sanitize:

```powershell
& $BlenderExe --command extension --help
& $BlenderExe --command extension repo-add --help
& $BlenderExe --command extension install-file --help
& $BlenderExe --command extension list --help
& $BlenderExe --command extension remove --help
```

Also capture `extension list` with:

* no Agentic Blender package
* Agentic Blender installed and enabled
* Agentic Blender installed and disabled
* one unrelated package

Commit only stable, sanitized fixtures needed by parsers. Do not commit machine paths or user names.

## 14.4 PowerShell Build Helper

Create `scripts/build_extension.ps1`.

```powershell
<#
.SYNOPSIS
    Validate and build the bundled Agentic Blender extension.

.PARAMETER BlenderExe
    Optional path to blender.exe.

.PARAMETER OutputDir
    Output directory. Defaults to dist\extension.

.EXAMPLE
    .\scripts\build_extension.ps1

.EXAMPLE
    .\scripts\build_extension.ps1 `
        -BlenderExe "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
#>

[CmdletBinding()]
param (
    [string]$BlenderExe = "",
    [string]$OutputDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $repoRoot "src\agentic_blender\resources\blender_extension"

if (-not $BlenderExe) {
    $pathCommand = Get-Command "blender.exe" -ErrorAction SilentlyContinue
    if ($pathCommand) {
        $BlenderExe = $pathCommand.Source
    }
}

if (-not $BlenderExe) {
    $roots = @()

    if ($env:ProgramFiles) {
        $roots += Join-Path $env:ProgramFiles "Blender Foundation"
    }

    if (${env:ProgramFiles(x86)}) {
        $roots += Join-Path ${env:ProgramFiles(x86)} "Blender Foundation"
    }

    if ($env:LOCALAPPDATA) {
        $roots += Join-Path $env:LOCALAPPDATA "Programs\Blender Foundation"
    }

    $BlenderExe = $roots |
        Where-Object { Test-Path -LiteralPath $_ } |
        ForEach-Object {
            Get-ChildItem -LiteralPath $_ -Directory -ErrorAction SilentlyContinue
        } |
        ForEach-Object {
            Join-Path $_.FullName "blender.exe"
        } |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        Sort-Object -Descending |
        Select-Object -First 1
}

if (-not $BlenderExe -or -not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "blender.exe was not found. Pass -BlenderExe explicitly."
}

if (-not $OutputDir) {
    $OutputDir = Join-Path $repoRoot "dist\extension"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$manifestPath = Join-Path $sourceDir "blender_manifest.toml"
$manifestText = Get-Content -LiteralPath $manifestPath -Raw
$versionMatch = [regex]::Match(
    $manifestText,
    '(?m)^version\s*=\s*"([^"]+)"\s*$'
)

if (-not $versionMatch.Success) {
    throw "Could not read the extension version from blender_manifest.toml."
}

$version = $versionMatch.Groups[1].Value
$artifact = Join-Path $OutputDir "agentic_blender-$version.zip"

& $BlenderExe --command extension validate $sourceDir
if ($LASTEXITCODE -ne 0) {
    throw "Extension source validation failed with exit code $LASTEXITCODE."
}

if (Test-Path -LiteralPath $artifact) {
    Remove-Item -LiteralPath $artifact -Force
}

& $BlenderExe --command extension build `
    --source-dir $sourceDir `
    --output-filepath $artifact

if ($LASTEXITCODE -ne 0) {
    throw "Extension build failed with exit code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
    throw "Build completed without producing $artifact."
}

& $BlenderExe --command extension validate $artifact
if ($LASTEXITCODE -ne 0) {
    throw "Built extension validation failed with exit code $LASTEXITCODE."
}

Write-Output $artifact
```

The helper:

* uses PowerShell path handling
* searches `PATH` before standard roots
* uses environment-based standard roots
* validates source and archive
* creates an exact artifact path
* prints only the final artifact path as pipeline output
* never installs or removes an extension

---

## 15. Test Layout

```text
tests/
+-- blender/
|   +-- __init__.py
|   +-- conftest.py
|   +-- test_command.py
|   +-- test_discovery.py
|   +-- test_process.py
|   +-- test_extension_resources.py
|   +-- test_extension.py
|   +-- test_extension_blender.py
+-- fixtures/
|   +-- blender_5_2_extension_list.txt
|   +-- dummy_extension/
|       +-- __init__.py
|       +-- blender_manifest.toml
+-- resources/
    +-- test_extension_manifest.py
```

Marker policy:

* `unit`: pure logic and mocked process calls
* `integration`: filesystem staging, wheel inspection, and config round trips
* `blender`: real Blender executable with isolated user directories

The existing quality script runs:

```powershell
uv run pytest tests/ -m "unit or integration"
```

Real-Blender tests run separately:

```powershell
$env:BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
uv run pytest tests/blender/test_extension_blender.py -m blender -v
```

---

## 16. Quality Gate

After each step:

```powershell
.\scripts\quality.ps1
```

Before merge:

```powershell
uv run pytest tests/blender/test_extension_blender.py -m blender -v
.\scripts\build_extension.ps1 -BlenderExe $env:BLENDER_EXE
uv build
```

Required results:

```text
ruff format --check .                 0 violations
ruff check .                          0 violations
mypy src/agentic_blender/             0 errors
pytest -m "unit or integration"       all pass
coverage                              >= 70%
pre-commit                            all pass
Blender manifest source validation   pass
Blender archive validation            pass
Blender lifecycle tests               pass in isolated profile
wheel resource inspection             pass
```

---

## 17. Task Traceability

| Task       | Implementation                                                |
| ---------- | ------------------------------------------------------------- |
| BLD-001    | `BlenderInstall`, discovery result, and inspection interfaces |
| BLD-002    | Environment-derived Windows standard roots                    |
| BLD-003    | Existing `BlenderConfig.search_paths` expansion               |
| BLD-004    | Non-empty `blender.exe` validation                            |
| BLD-005    | Shared bounded subprocess runner and `--version`              |
| BLD-006    | Anchored version parser                                       |
| BLD-007    | Existing Phase 1 5.2.0 classification                         |
| BLD-008    | Later 5.2.x remains `UNVERIFIED`                              |
| BLD-009    | Newer versions remain `UNVERIFIED`                            |
| BLD-010    | Unsupported issue with remediation context                    |
| BLD-011    | Deterministic multi-install ordering and preferred selection  |
| BLD-012    | Nested `config.blender.executable` persistence                |
| BLD-013    | Discovery and parsing tests                                   |
| PROC-001   | `psutil.process_iter` discovery                               |
| PROC-002   | Resolved executable identity                                  |
| PROC-003   | Dead PID, zombie, access denied, and PID reuse detection      |
| PROC-004   | `SessionMetadata.blender_pid` association                     |
| PROC-005   | Connected, disconnected, stale wrapper state                  |
| PROC-006   | Explicit ambiguity failure for multiple connected instances   |
| PROC-007   | Mocked psutil tests                                           |
| EXTSRC-001 | Bundled `resources/blender_extension` directory               |
| EXTSRC-002 | Valid 5.2.0 manifest                                          |
| EXTSRC-003 | Root `__init__.py` register/unregister                        |
| EXTSRC-004 | UI preferences aligned with Phase 1 config                    |
| EXTSRC-005 | Manifest/project version equality test                        |
| EXTSRC-006 | Standard library and Blender-only imports                     |
| EXTINS-001 | Parent-package `importlib.resources` staging                  |
| EXTINS-002 | Source/archive validation and exact ZIP build                 |
| EXTINS-003 | Dedicated-repository `install-file`                           |
| EXTINS-004 | Install `--enable` and Blender-side enable operation          |
| EXTINS-005 | Parsed installed-package state                                |
| EXTINS-006 | Blender-side enabled-state JSON probe                         |
| EXTINS-007 | Exact-version no-op, re-enable, and upgrade path              |
| EXTINS-008 | Verified idempotent package removal                           |
| EXTINS-009 | Dedicated target plus unrelated-extension lifecycle test      |
| EXTINS-010 | Safe PowerShell validation/build helper                       |

---

## 18. Final Exit Checklist

### Discovery

* [ ] Existing nested Blender configuration is reused.
* [ ] Candidate collection is bounded and deterministic.
* [ ] Standard roots are environment-derived.
* [ ] `PATH` discovery is supported.
* [ ] Case-insensitive path deduplication works.
* [ ] Candidate failures are reported without aborting the search.
* [ ] Unsupported versions are never returned as usable.
* [ ] Configured usable executable remains preferred.
* [ ] Persistence updates only `config.blender.executable`.

### Process Discovery

* [ ] Existing `BlenderProcess` is reused.
* [ ] Existing `SessionMetadata` is reused.
* [ ] Executable path is authoritative.
* [ ] PID reuse becomes stale registration metadata.
* [ ] Connected state requires a matching live PID and session.
* [ ] Multiple connected instances require explicit selection.

### Extension Source

* [ ] Archive root uses `__init__.py`.
* [ ] No `__init_extension__.py`.
* [ ] No `bl_info`.
* [ ] Preferences use `__package__`.
* [ ] No host or port preference.
* [ ] No network permission.
* [ ] Manifest source validates without warnings.
* [ ] Extension files are present in the wheel.

### Extension Lifecycle

* [ ] Resources are staged recursively from `Traversable`.
* [ ] Build uses `--output-filepath`.
* [ ] Source and archive are validated.
* [ ] `install-file` includes `--repo`.
* [ ] Dedicated repository creation is idempotent.
* [ ] Enabled state uses a full extension module name.
* [ ] Exact installed+enabled version is a no-op.
* [ ] Disabled exact version is enabled without rebuilding.
* [ ] Upgrade failure does not remove the existing extension.
* [ ] Removal targets only Agentic Blender.
* [ ] Unrelated extension and repository survive lifecycle tests.
* [ ] Automated Blender tests use isolated user directories.

### Quality

* [ ] Unit tests pass.
* [ ] Integration tests pass.
* [ ] Blender tests pass on 5.2.0 LTS.
* [ ] Ruff passes for external and extension code.
* [ ] Mypy passes for external code.
* [ ] Coverage remains at least 70%.
* [ ] Pre-commit passes.
* [ ] PowerShell helper prints the exact validated artifact.
