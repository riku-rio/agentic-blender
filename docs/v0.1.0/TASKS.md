# Agentic Blender v0.1.0 Implementation Tasks

## Document Status

- **Version:** v0.1.0
- **Status:** Draft
- **Date:** 2026-07-22
- **Source:** [PRD.md](./PRD.md)
- **Official Blender target:** Blender 5.2.0 LTS
- **Official platform target:** Windows 10/11 x64

## 1. Purpose

This document translates the v0.1.0 product requirements into an ordered implementation plan.

Tasks are grouped by delivery phase and use stable identifiers so they can later be converted into GitHub issues without losing traceability.

A checked task means its implementation, tests, and relevant documentation are complete. Code existing locally is not enough to mark a task complete.

## 2. Completion Rules

A task may be checked only when all applicable conditions are true:

- The implementation is committed.
- Relevant tests pass.
- Failure behavior is covered where practical.
- User-facing behavior matches the PRD.
- Public interfaces are documented.
- Important tradeoffs are recorded in `decisions/`.
- No known blocker remains for the task's acceptance criteria.

## 3. Delivery Order

The intended implementation order is:

```text
Phase 0: Decisions and repository foundation
Phase 1: Core models, configuration, and runtime paths
Phase 2: Blender discovery and extension packaging
Phase 3: IPC, sessions, and extension bridge
Phase 4: CLI setup and diagnostics
Phase 5: MCP server and tool contracts
Phase 6: Blender scene tools
Phase 7: Screenshot and export
Phase 8: Extension workflow UI
Phase 9: Generic agent skill and help documentation
Phase 10: End-to-end verification and release readiness
```

Later phases may begin before all earlier phases are complete when dependencies are clear, but the release must preserve the architectural boundaries defined by the PRD and decision records.

---

# Phase 0 — Decisions and Repository Foundation

## 0.1 Decision Records

- [x] **DEC-001** Create `docs/v0.1.0/decisions/0001-project-name.md`.
  - Record the decision to use `agentic-blender`.
  - Record the Python import name `agentic_blender`.
  - Document rejected alternatives including `blender-mcp`.

- [x] **DEC-002** Create `docs/v0.1.0/decisions/0002-supported-environment.md`.
  - Record Windows 10/11 x64 as the v0.1.0 platform.
  - Record Blender 5.2.0 LTS as the official target.
  - Record Python 3.10+ support and Python 3.11 development target.

- [x] **DEC-003** Create `docs/v0.1.0/decisions/0003-python-and-uv-toolchain.md`.
  - Record Python as the only implementation language in v0.1.0.
  - Record `uv` and `uv_build` choices.
  - Record why Node.js, TypeScript, Rust, and C++ are excluded.

- [x] **DEC-004** Create `docs/v0.1.0/decisions/0004-mcp-stdio-transport.md`.
  - Record `stdio` as the only MCP transport in v0.1.0.
  - Record the canonical server identity.
  - Record why HTTP, SSE, WebSocket, and TCP MCP transports are excluded.

- [x] **DEC-005** Create `docs/v0.1.0/decisions/0005-blender-extension-bridge.md`.
  - Record the external MCP server and in-Blender extension split.
  - Record the Blender main-thread execution requirement.
  - Record zero third-party extension dependencies.

- [x] **DEC-006** Create `docs/v0.1.0/decisions/0006-file-based-ipc.md`.
  - Define why file-based IPC is selected for v0.1.0.
  - Define command, response, heartbeat, and status files.
  - Document future migration possibilities without committing to them.

- [x] **DEC-007** Create `docs/v0.1.0/decisions/0007-open-blender-reuse-policy.md`.
  - Record reuse of an already-connected Blender instance.
  - Record unsaved-work protection.
  - Record behavior for running but disconnected Blender instances.
  - Record multiple-instance selection policy once finalized.

- [x] **DEC-008** Create `docs/v0.1.0/decisions/0008-add-primitive-tool.md`.
  - Record one general `add_primitive` tool.
  - Record the supported primitive names and convenience aliases.
  - Record why separate primitive tools are rejected.

- [x] **DEC-009** Create `docs/v0.1.0/decisions/0009-window-screenshot-strategy.md`.
  - Record `pywin32`, `mss`, and Pillow responsibilities.
  - Record full Blender-window capture as the required mode.
  - Record DPI and multi-monitor expectations.

- [x] **DEC-010** Create `docs/v0.1.0/decisions/0010-export-as-blend-save.md`.
  - Record that the public tool is named `export`.
  - Clarify that Blender implementation uses normal `.blend` project saving.
  - Record overwrite protection and verification behavior.

- [x] **DEC-011** Create `docs/v0.1.0/decisions/0011-agent-workflow.md`.
  - Record Plan → Review → Implement → Verify → Export → Report.
  - Record the three-attempt limits.
  - Record programmatic and visual verification responsibilities.

- [x] **DEC-012** Create `docs/v0.1.0/decisions/0012-generic-skill-distribution.md`.
  - Record that the project remains agent-agnostic.
  - Record distribution of one generic `SKILL.md`.
  - Record absence of product-specific agent metadata in v0.1.0.

- [x] **DEC-013** Create `docs/v0.1.0/decisions/0013-license.md`.
  - Confirm the project license.
  - Document compatibility considerations for the Blender extension.

## 0.2 Repository Bootstrap

- [ ] **REP-001** Initialize the packaged Python project with `uv`.
- [ ] **REP-002** Configure the `src/agentic_blender/` package layout.
- [ ] **REP-003** Pin the development Python version to 3.11.
- [ ] **REP-004** Set `requires-python = ">=3.10"`.
- [ ] **REP-005** Configure `uv_build` as the build backend.
- [ ] **REP-006** Add and lock runtime dependencies.
- [ ] **REP-007** Add and lock development dependencies.
- [ ] **REP-008** Commit `uv.lock` and `.python-version`.
- [ ] **REP-009** Add a Windows-appropriate `.gitignore`.
- [ ] **REP-010** Add the selected open-source license.
- [ ] **REP-011** Add `CHANGELOG.md` with an unreleased v0.1.0 section.
- [ ] **REP-012** Add `CONTRIBUTING.md`.
- [ ] **REP-013** Add root `SECURITY.md` with responsible disclosure guidance.

## 0.3 Tooling and Quality

- [ ] **QLT-001** Configure Ruff formatting.
- [ ] **QLT-002** Configure Ruff lint rules.
- [ ] **QLT-003** Configure mypy for the external Python package.
- [ ] **QLT-004** Define the relaxed or excluded type-checking policy for Blender-specific modules.
- [ ] **QLT-005** Configure pytest.
- [ ] **QLT-006** Configure pytest-asyncio.
- [ ] **QLT-007** Configure pytest-cov.
- [ ] **QLT-008** Configure pre-commit hooks.
- [ ] **QLT-009** Add a local quality command documented for contributors.
- [ ] **QLT-010** Add GitHub Actions CI for supported external Python versions.
- [ ] **QLT-011** Ensure CI does not pretend to run Blender GUI tests on unsupported runners.
- [ ] **QLT-012** Add a separate manual or self-hosted workflow strategy for Blender smoke tests.

### Phase 0 Exit Criteria

- [ ] All foundational decisions required before implementation are accepted or explicitly marked proposed.
- [ ] The project installs with `uv sync`.
- [ ] Formatting, linting, typing, and unit test commands run successfully.
- [ ] CI runs on a minimal repository commit.

---

# Phase 1 — Core Models, Configuration, and Runtime Paths

## 1.1 Package Structure

- [ ] **CORE-001** Create `src/agentic_blender/__init__.py`.
- [ ] **CORE-002** Add a central version constant or package metadata lookup.
- [ ] **CORE-003** Create packages for:
  - `models/`
  - `ipc/`
  - `blender/`
  - `tools/`
  - `capture/`
  - `platform/windows/`
  - `mcp_adapter/`
  - `resources/`

## 1.2 Configuration

- [ ] **CFG-001** Define the application configuration model with Pydantic.
- [ ] **CFG-002** Define configuration precedence:
  - CLI arguments.
  - Environment variables.
  - Configuration file.
  - Defaults.
- [ ] **CFG-003** Define Blender installation configuration.
- [ ] **CFG-004** Define timeout configuration.
- [ ] **CFG-005** Define screenshot defaults.
- [ ] **CFG-006** Define extension UI preferences where externally configurable.
- [ ] **CFG-007** Define safe config serialization and loading.
- [ ] **CFG-008** Handle malformed configuration with a stable error.
- [ ] **CFG-009** Prevent secrets from being persisted in long-lived configuration.

## 1.3 Application Paths

- [ ] **PATH-001** Use `platformdirs` for config, data, cache, and log roots.
- [ ] **PATH-002** Define runtime and session directory layout.
- [ ] **PATH-003** Define extension bundle staging path.
- [ ] **PATH-004** Implement directory creation with actionable errors.
- [ ] **PATH-005** Validate writable runtime and log locations.
- [ ] **PATH-006** Implement safe path normalization for Windows.
- [ ] **PATH-007** Support spaces and non-ASCII characters in user paths.
- [ ] **PATH-008** Add unit tests for path resolution and creation.

## 1.4 Shared Models

- [ ] **MOD-001** Define `Vector3` and transform models.
- [ ] **MOD-002** Define Blender version and support-state models.
- [ ] **MOD-003** Define Blender process and window identity models.
- [ ] **MOD-004** Define session metadata models.
- [ ] **MOD-005** Define heartbeat models.
- [ ] **MOD-006** Define workflow status models.
- [ ] **MOD-007** Define command envelope models.
- [ ] **MOD-008** Define response envelope models.
- [ ] **MOD-009** Define structured error models.
- [ ] **MOD-010** Define scene summary and object summary models.
- [ ] **MOD-011** Define screenshot result models.
- [ ] **MOD-012** Define export result models.
- [ ] **MOD-013** Add serialization round-trip tests for all IPC models.
- [ ] **MOD-014** Reject unknown or unsupported command types.

## 1.5 Error System

- [ ] **ERR-001** Create a central error-code enumeration.
- [ ] **ERR-002** Implement at least these codes:
  - `BLENDER_NOT_FOUND`
  - `BLENDER_UNSUPPORTED_VERSION`
  - `BLENDER_NOT_CONNECTED`
  - `BLENDER_START_TIMEOUT`
  - `BLENDER_DISCONNECTED`
  - `UNSAVED_CHANGES`
  - `OBJECT_NOT_FOUND`
  - `UNSUPPORTED_PRIMITIVE`
  - `INVALID_OUTPUT_PATH`
  - `OUTPUT_ALREADY_EXISTS`
  - `SCREENSHOT_FAILED`
  - `EXPORT_FAILED`
  - `COMMAND_TIMEOUT`
  - `INVALID_SESSION`
- [ ] **ERR-003** Define human-readable messages and suggested actions.
- [ ] **ERR-004** Ensure exceptions are converted to structured failures at boundaries.
- [ ] **ERR-005** Add tests for stable error serialization.

### Phase 1 Exit Criteria

- [ ] Configuration loads and validates.
- [ ] Runtime paths are created safely.
- [ ] Shared models round-trip through JSON.
- [ ] Stable errors are available to CLI, MCP, and IPC layers.

---

# Phase 2 — Blender Discovery and Extension Packaging

## 2.1 Blender Discovery

- [ ] **BLD-001** Define the Blender installation discovery interface.
- [ ] **BLD-002** Search standard Windows installation locations.
- [ ] **BLD-003** Search configured custom paths.
- [ ] **BLD-004** Validate discovered executables.
- [ ] **BLD-005** Run `blender.exe --version` safely.
- [ ] **BLD-006** Parse Blender version output.
- [ ] **BLD-007** Recognize Blender 5.2.0 LTS as supported.
- [ ] **BLD-008** Define behavior for later 5.2.x LTS patch releases.
- [ ] **BLD-009** Mark newer versions unverified or experimental.
- [ ] **BLD-010** Reject unsupported older versions with remediation.
- [ ] **BLD-011** Handle multiple supported installations.
- [ ] **BLD-012** Persist the selected installation.
- [ ] **BLD-013** Add discovery and version parsing tests.

## 2.2 Running Process Discovery

- [ ] **PROC-001** Use `psutil` to discover running Blender processes.
- [ ] **PROC-002** Verify executable identity rather than process name alone.
- [ ] **PROC-003** Detect stale process metadata.
- [ ] **PROC-004** Associate connected extension registrations with process IDs.
- [ ] **PROC-005** Distinguish connected, disconnected, and stale instances.
- [ ] **PROC-006** Define deterministic behavior when multiple connected instances exist.
- [ ] **PROC-007** Add tests using mocked process metadata.

## 2.3 Extension Source

- [ ] **EXTSRC-001** Create the bundled extension directory.
- [ ] **EXTSRC-002** Create `blender_manifest.toml` targeting Blender 5.2.0 LTS.
- [ ] **EXTSRC-003** Add extension registration and unregistration.
- [ ] **EXTSRC-004** Add extension preferences.
- [ ] **EXTSRC-005** Add version metadata aligned with the Python package.
- [ ] **EXTSRC-006** Ensure the extension has no third-party dependencies.

## 2.4 Extension Build and Installation

- [ ] **EXTINS-001** Implement extension bundle discovery through `importlib.resources`.
- [ ] **EXTINS-002** Implement extension build or packaging.
- [ ] **EXTINS-003** Implement installation into the selected Blender 5.2.0 LTS instance.
- [ ] **EXTINS-004** Implement extension enablement.
- [ ] **EXTINS-005** Verify that the extension is installed.
- [ ] **EXTINS-006** Verify that the extension is enabled.
- [ ] **EXTINS-007** Implement idempotent reinstall or upgrade behavior.
- [ ] **EXTINS-008** Implement safe extension removal.
- [ ] **EXTINS-009** Preserve unrelated Blender extensions and preferences.
- [ ] **EXTINS-010** Add a PowerShell helper for manual extension build testing.

### Phase 2 Exit Criteria

- [ ] A supported Blender installation is detected and selected.
- [ ] The extension can be built, installed, enabled, verified, and removed.
- [ ] Re-running installation does not corrupt Blender configuration.

---

# Phase 3 — IPC, Sessions, and Extension Bridge

## 3.1 IPC Protocol Definition

- [ ] **IPC-001** Create `docs/ipc-protocol.md`.
- [ ] **IPC-002** Define session directory layout.
- [ ] **IPC-003** Define command file naming.
- [ ] **IPC-004** Define response file naming.
- [ ] **IPC-005** Define heartbeat file schema.
- [ ] **IPC-006** Define workflow status file schema.
- [ ] **IPC-007** Define command lifecycle states.
- [ ] **IPC-008** Define response lifecycle and cleanup.
- [ ] **IPC-009** Define stale-message behavior.
- [ ] **IPC-010** Define protocol versioning.

## 3.2 Atomic File Operations

- [ ] **IPC-011** Implement atomic JSON writes using temporary files and replacement.
- [ ] **IPC-012** Implement strict JSON reads.
- [ ] **IPC-013** Handle partially written or malformed files.
- [ ] **IPC-014** Ensure command files are processed at most once.
- [ ] **IPC-015** Implement bounded polling.
- [ ] **IPC-016** Implement cleanup of expired messages.
- [ ] **IPC-017** Add tests for interrupted writes and stale files.

## 3.3 Session Management

- [ ] **SES-001** Generate unique session identifiers.
- [ ] **SES-002** Generate unpredictable session authentication data.
- [ ] **SES-003** Create per-session directories.
- [ ] **SES-004** Write session metadata atomically.
- [ ] **SES-005** Validate session identity on every command.
- [ ] **SES-006** Detect stale sessions.
- [ ] **SES-007** Close sessions cleanly.
- [ ] **SES-008** Recover from an MCP server restart where possible.
- [ ] **SES-009** Prevent session secrets from appearing in logs.
- [ ] **SES-010** Add session lifecycle tests.

## 3.4 Launch Locking

- [ ] **LOCK-001** Implement a Blender launch lock using `filelock`.
- [ ] **LOCK-002** Implement a session registry lock.
- [ ] **LOCK-003** Implement an extension install lock.
- [ ] **LOCK-004** Add timeout and stale-lock behavior.
- [ ] **LOCK-005** Add concurrency tests.

## 3.5 Extension Bridge Runtime

- [ ] **BRG-001** Register the Blender process and version.
- [ ] **BRG-002** Publish periodic heartbeat updates.
- [ ] **BRG-003** Poll the active session command inbox using `bpy.app.timers`.
- [ ] **BRG-004** Validate protocol version.
- [ ] **BRG-005** Validate session identity and authentication data.
- [ ] **BRG-006** Dispatch only allowlisted commands.
- [ ] **BRG-007** Execute Blender operations on the main thread.
- [ ] **BRG-008** Serialize successful results.
- [ ] **BRG-009** Serialize structured failures.
- [ ] **BRG-010** Record command timestamps and durations.
- [ ] **BRG-011** Avoid processing duplicate command IDs.
- [ ] **BRG-012** Stop timers cleanly during extension unregister.
- [ ] **BRG-013** Re-register after Blender file changes when required.
- [ ] **BRG-014** Add bridge diagnostic logging.

## 3.6 External IPC Client

- [ ] **IPCC-001** Implement command creation.
- [ ] **IPCC-002** Implement response waiting with timeout.
- [ ] **IPCC-003** Detect Blender disconnection during a wait.
- [ ] **IPCC-004** Convert protocol failures to shared errors.
- [ ] **IPCC-005** Support cancellation and cleanup.
- [ ] **IPCC-006** Add integration tests with a fake bridge.

### Phase 3 Exit Criteria

- [ ] A fake client and fake bridge can exchange typed commands and responses.
- [ ] Blender publishes a live heartbeat.
- [ ] The extension executes a safe test command on Blender's main thread.
- [ ] Invalid sessions and commands are rejected.

---

# Phase 4 — CLI Setup and Diagnostics

## 4.1 CLI Foundation

- [ ] **CLI-001** Create the Typer application.
- [ ] **CLI-002** Configure Rich output.
- [ ] **CLI-003** Add consistent exit codes.
- [ ] **CLI-004** Add global verbosity or logging options.
- [ ] **CLI-005** Ensure CLI failures never emit raw tracebacks by default.
- [ ] **CLI-006** Add CLI unit tests with isolated filesystem state.

## 4.2 `agentic-blender init`

- [ ] **INIT-001** Detect Blender installations.
- [ ] **INIT-002** Allow supported installation selection.
- [ ] **INIT-003** Create required application directories.
- [ ] **INIT-004** Save configuration.
- [ ] **INIT-005** Build and install the extension.
- [ ] **INIT-006** Enable the extension.
- [ ] **INIT-007** Launch Blender when required for verification.
- [ ] **INIT-008** Attempt a bridge handshake.
- [ ] **INIT-009** Print canonical MCP registration data.
- [ ] **INIT-010** Print generic skill installation guidance.
- [ ] **INIT-011** Provide a final success and warning summary.
- [ ] **INIT-012** Make repeated initialization idempotent.
- [ ] **INIT-013** Test clean installation behavior.
- [ ] **INIT-014** Test reinitialization behavior.

## 4.3 `agentic-blender doctor`

- [ ] **DOC-001** Check external Python version.
- [ ] **DOC-002** Check package installation and version.
- [ ] **DOC-003** Check configuration validity.
- [ ] **DOC-004** Check Blender executable existence.
- [ ] **DOC-005** Check Blender version and support state.
- [ ] **DOC-006** Check extension installation.
- [ ] **DOC-007** Check extension enablement.
- [ ] **DOC-008** Check application directory permissions.
- [ ] **DOC-009** Check session directory permissions.
- [ ] **DOC-010** Check log directory permissions.
- [ ] **DOC-011** Check `pywin32` availability.
- [ ] **DOC-012** Check `mss` availability.
- [ ] **DOC-013** Check Pillow PNG support.
- [ ] **DOC-014** Check bridge heartbeat when Blender is open.
- [ ] **DOC-015** Execute a safe bridge test command when connected.
- [ ] **DOC-016** Provide remediation for each failure.
- [ ] **DOC-017** Define safe `doctor --fix` actions.
- [ ] **DOC-018** Ensure destructive fixes require confirmation.
- [ ] **DOC-019** Add tests for pass, warning, and failure reports.

## 4.4 `agentic-blender status`

- [ ] **STAT-001** Show configured Blender path and version.
- [ ] **STAT-002** Show discovered running Blender processes.
- [ ] **STAT-003** Show connected extension instance.
- [ ] **STAT-004** Show active session.
- [ ] **STAT-005** Show workflow state.
- [ ] **STAT-006** Show heartbeat age.
- [ ] **STAT-007** Distinguish ready, disconnected, and stale states.

## 4.5 `agentic-blender mcp`

- [ ] **MCPCLI-001** Start the MCP server over stdio.
- [ ] **MCPCLI-002** Keep stdout reserved for MCP protocol output.
- [ ] **MCPCLI-003** Send logs to stderr or files.
- [ ] **MCPCLI-004** Handle clean shutdown.
- [ ] **MCPCLI-005** Return a non-zero exit code on startup failure.

## 4.6 `agentic-blender help`

- [ ] **HELP-001** Add general help.
- [ ] **HELP-002** Add setup help.
- [ ] **HELP-003** Add MCP registration help.
- [ ] **HELP-004** Add skill help.
- [ ] **HELP-005** Add tools help.
- [ ] **HELP-006** Add workflow help.
- [ ] **HELP-007** Display `uv tool run` as the canonical form.
- [ ] **HELP-008** Display `uvx` as an equivalent shorthand.
- [ ] **HELP-009** Add canonical JSON descriptor output.
- [ ] **HELP-010** Add a machine-readable output option if useful.

## 4.7 Skill Copy and Uninstall

- [ ] **SKCLI-001** Print the bundled `SKILL.md`.
- [ ] **SKCLI-002** Copy `SKILL.md` to a user-selected path.
- [ ] **SKCLI-003** Refuse accidental overwrite by default.
- [ ] **UNINS-001** Remove the Blender extension.
- [ ] **UNINS-002** Remove managed runtime data when requested.
- [ ] **UNINS-003** Preserve config or logs based on explicit options.
- [ ] **UNINS-004** Preserve unrelated Blender and user data.

### Phase 4 Exit Criteria

- [ ] The full local setup can be performed using CLI commands only.
- [ ] `doctor` produces actionable output.
- [ ] `status` accurately reflects Blender and bridge state.
- [ ] MCP and skill instructions remain product-agnostic.

---

# Phase 5 — MCP Server and Tool Contracts

## 5.1 MCP Adapter

- [ ] **MCPA-001** Create the MCP adapter boundary.
- [ ] **MCPA-002** Pin the stable MCP SDK v1 line below v2.
- [ ] **MCPA-003** Initialize `FastMCP` or the selected official v1 server API.
- [ ] **MCPA-004** Register the canonical server name `agentic-blender`.
- [ ] **MCPA-005** Implement structured tool results.
- [ ] **MCPA-006** Convert shared errors to MCP-safe results.
- [ ] **MCPA-007** Support image content for screenshots.
- [ ] **MCPA-008** Add protocol-focused tests without Blender.

## 5.2 Tool Input Models

- [ ] **TOOLM-001** Define `open_blender` inputs.
- [ ] **TOOLM-002** Define `delete_object` inputs.
- [ ] **TOOLM-003** Define `add_primitive` inputs.
- [ ] **TOOLM-004** Define `inspect_scene` inputs, if any.
- [ ] **TOOLM-005** Define `screenshot` inputs.
- [ ] **TOOLM-006** Define `export` inputs.
- [ ] **TOOLM-007** Validate all path and filename fields.
- [ ] **TOOLM-008** Validate transforms and primitive-specific values.

## 5.3 Tool Result Models

- [ ] **TOOLR-001** Define Blender readiness result.
- [ ] **TOOLR-002** Define object deletion result.
- [ ] **TOOLR-003** Define primitive creation result.
- [ ] **TOOLR-004** Define scene inspection result.
- [ ] **TOOLR-005** Define screenshot result.
- [ ] **TOOLR-006** Define export result.
- [ ] **TOOLR-007** Ensure all successful results include relevant session context.
- [ ] **TOOLR-008** Ensure all failures include stable error codes.

## 5.4 MCP Tool Registration

- [ ] **MCPTOOL-001** Register `open_blender`.
- [ ] **MCPTOOL-002** Register `delete_object`.
- [ ] **MCPTOOL-003** Register `add_primitive`.
- [ ] **MCPTOOL-004** Register `inspect_scene`.
- [ ] **MCPTOOL-005** Register `screenshot`.
- [ ] **MCPTOOL-006** Register `export`.
- [ ] **MCPTOOL-007** Verify that no arbitrary execution tool is exposed.
- [ ] **MCPTOOL-008** Add tool schema snapshot tests.

### Phase 5 Exit Criteria

- [ ] An MCP client can discover all six tools.
- [ ] Tool schemas are typed and documented.
- [ ] Tool errors are deterministic.
- [ ] No tool permits arbitrary Python, shell, or Blender script execution.

---

# Phase 6 — Blender Launching and Scene Tools

## 6.1 Blender Launcher

- [ ] **LAUNCH-001** Launch the configured Blender executable as a GUI application.
- [ ] **LAUNCH-002** Never use background mode in the primary workflow.
- [ ] **LAUNCH-003** Pass runtime/session information safely.
- [ ] **LAUNCH-004** Wait for process startup.
- [ ] **LAUNCH-005** Wait for extension heartbeat.
- [ ] **LAUNCH-006** Apply a bounded startup timeout.
- [ ] **LAUNCH-007** Terminate only processes started by Agentic Blender when cleanup is required.
- [ ] **LAUNCH-008** Return structured startup failures.

## 6.2 `open_blender`

- [ ] **OPEN-001** Detect connected running instances.
- [ ] **OPEN-002** Reuse an existing connected instance.
- [ ] **OPEN-003** Avoid duplicate launches on repeated calls.
- [ ] **OPEN-004** Detect running but disconnected Blender instances.
- [ ] **OPEN-005** Return `BLENDER_NOT_CONNECTED` for an unusable running instance.
- [ ] **OPEN-006** Detect unsaved changes.
- [ ] **OPEN-007** Return `UNSAVED_CHANGES` by default.
- [ ] **OPEN-008** Require explicit user authorization before discard.
- [ ] **OPEN-009** Create a new default project.
- [ ] **OPEN-010** Confirm expected default scene state.
- [ ] **OPEN-011** Restore and focus the Blender window where practical.
- [ ] **OPEN-012** Return reused-instance, process, version, and scene metadata.
- [ ] **OPEN-013** Add tests for closed Blender.
- [ ] **OPEN-014** Add tests for already-open connected Blender.
- [ ] **OPEN-015** Add tests for unsaved changes.
- [ ] **OPEN-016** Add tests for disconnected running Blender.

## 6.3 Extension Command Operations

- [ ] **OPS-001** Implement a new-project operation.
- [ ] **OPS-002** Implement unsaved-change inspection.
- [ ] **OPS-003** Implement scene inspection.
- [ ] **OPS-004** Implement object deletion.
- [ ] **OPS-005** Implement primitive creation.
- [ ] **OPS-006** Implement project saving.
- [ ] **OPS-007** Return consistent object summaries.
- [ ] **OPS-008** Preserve Blender context where possible.
- [ ] **OPS-009** Avoid selection-dependent behavior unless unavoidable.

## 6.4 `delete_object`

- [ ] **DEL-001** Delete an object by name or resolved data identity.
- [ ] **DEL-002** Support `fail_if_missing` behavior.
- [ ] **DEL-003** Return `OBJECT_NOT_FOUND` when required.
- [ ] **DEL-004** Return updated scene information.
- [ ] **DEL-005** Test deletion of `Cube`.
- [ ] **DEL-006** Test deletion of a missing object.

## 6.5 `add_primitive`

- [ ] **PRIM-001** Define the public primitive enumeration.
- [ ] **PRIM-002** Implement `cube`.
- [ ] **PRIM-003** Implement `sphere`.
- [ ] **PRIM-004** Implement `icosphere`.
- [ ] **PRIM-005** Implement `cylinder`.
- [ ] **PRIM-006** Implement `cone`.
- [ ] **PRIM-007** Implement `torus`.
- [ ] **PRIM-008** Implement `plane`.
- [ ] **PRIM-009** Implement `circle`.
- [ ] **PRIM-010** Implement `triangle`.
- [ ] **PRIM-011** Implement `square` alias behavior.
- [ ] **PRIM-012** Apply name, location, rotation, scale, and size.
- [ ] **PRIM-013** Validate optional segments, rings, vertices, and depth values.
- [ ] **PRIM-014** Return `UNSUPPORTED_PRIMITIVE` for unknown values.
- [ ] **PRIM-015** Return final object name and dimensions.
- [ ] **PRIM-016** Test standard sphere creation at the origin.
- [ ] **PRIM-017** Test convenience aliases.

## 6.6 `inspect_scene`

- [ ] **INSP-001** Return object names and types.
- [ ] **INSP-002** Return transforms.
- [ ] **INSP-003** Return dimensions when available.
- [ ] **INSP-004** Return active object.
- [ ] **INSP-005** Return mesh count.
- [ ] **INSP-006** Return current project path.
- [ ] **INSP-007** Return unsaved-change state.
- [ ] **INSP-008** Return Blender version.
- [ ] **INSP-009** Ensure the sphere acceptance state is machine-verifiable.
- [ ] **INSP-010** Add deterministic scene summary tests.

### Phase 6 Exit Criteria

- [ ] Blender opens or is reused safely.
- [ ] The default cube can be removed.
- [ ] A sphere can be added through `add_primitive`.
- [ ] `inspect_scene` verifies the expected result.

---

# Phase 7 — Screenshot and Export

## 7.1 Windows Window Discovery

- [ ] **WIN-001** Locate Blender windows by process ID.
- [ ] **WIN-002** Handle multiple windows for one process.
- [ ] **WIN-003** Confirm the selected window belongs to the active session process.
- [ ] **WIN-004** Detect minimized windows.
- [ ] **WIN-005** Restore minimized windows where practical.
- [ ] **WIN-006** Bring the window forward where permitted.
- [ ] **WIN-007** Read window bounds.
- [ ] **WIN-008** account for DPI scaling.
- [ ] **WIN-009** Support negative screen coordinates on multi-monitor setups.
- [ ] **WIN-010** Return a structured failure when no valid window is found.

## 7.2 `screenshot`

- [ ] **SHOT-001** Validate output directory.
- [ ] **SHOT-002** Create the output directory when policy permits.
- [ ] **SHOT-003** Sanitize optional filename.
- [ ] **SHOT-004** Generate timestamp-based filenames.
- [ ] **SHOT-005** Prevent accidental overwrite.
- [ ] **SHOT-006** Capture the complete Blender window with `mss`.
- [ ] **SHOT-007** Save a PNG.
- [ ] **SHOT-008** Validate the PNG with Pillow.
- [ ] **SHOT-009** Return width and height.
- [ ] **SHOT-010** Return absolute file path.
- [ ] **SHOT-011** Return MCP-compatible image content.
- [ ] **SHOT-012** Apply a bounded timeout.
- [ ] **SHOT-013** Return `SCREENSHOT_FAILED` with actionable context.
- [ ] **SHOT-014** Test normal window capture.
- [ ] **SHOT-015** Test minimized window behavior.
- [ ] **SHOT-016** Test scaled display behavior.
- [ ] **SHOT-017** Test multi-monitor coordinates.
- [ ] **SHOT-018** Test filename collision behavior.

## 7.3 `export`

- [ ] **EXP-001** Validate output directory.
- [ ] **EXP-002** Normalize and enforce `.blend` extension.
- [ ] **EXP-003** Generate timestamp-based filenames.
- [ ] **EXP-004** Prevent accidental overwrite.
- [ ] **EXP-005** Dispatch the Blender save operation.
- [ ] **EXP-006** Confirm the operation completed.
- [ ] **EXP-007** Verify that the file exists.
- [ ] **EXP-008** Verify non-zero file size.
- [ ] **EXP-009** Return absolute path and size.
- [ ] **EXP-010** Return scene summary and Blender version.
- [ ] **EXP-011** Return `EXPORT_FAILED` on failure.
- [ ] **EXP-012** Add a reopen validation script for Blender 5.2.0 LTS.
- [ ] **EXP-013** Test overwrite rejection.
- [ ] **EXP-014** Test timestamp filename behavior.

### Phase 7 Exit Criteria

- [ ] A valid Blender window screenshot is produced.
- [ ] Screenshot output can be consumed by an MCP visual reviewer.
- [ ] A non-empty `.blend` file is saved and reopens in Blender 5.2.0 LTS.

---

# Phase 8 — Extension Workflow UI

## 8.1 Workflow Status Storage

- [ ] **WFUI-001** Define the status payload consumed by the extension.
- [ ] **WFUI-002** Include task summary.
- [ ] **WFUI-003** Include workflow phase.
- [ ] **WFUI-004** Include current step.
- [ ] **WFUI-005** Include attempt and maximum attempts.
- [ ] **WFUI-006** Include latest action.
- [ ] **WFUI-007** Include failure reason.
- [ ] **WFUI-008** Include update timestamp.
- [ ] **WFUI-009** Detect stale status.

## 8.2 Sidebar Panel

- [ ] **PANEL-001** Add an `Agentic Blender` tab in the 3D Viewport sidebar.
- [ ] **PANEL-002** Display connection state.
- [ ] **PANEL-003** Display `Agent is working` state.
- [ ] **PANEL-004** Display task summary.
- [ ] **PANEL-005** Display workflow phase.
- [ ] **PANEL-006** Display current step.
- [ ] **PANEL-007** Display attempt count.
- [ ] **PANEL-008** Display latest action.
- [ ] **PANEL-009** Display failure reason.
- [ ] **PANEL-010** Display disconnected and stale states clearly.

## 8.3 Viewport Banner

- [ ] **BANNER-001** Implement a lightweight viewport draw handler.
- [ ] **BANNER-002** Draw `Agentic Blender — Agent is working`.
- [ ] **BANNER-003** Draw the current workflow step.
- [ ] **BANNER-004** Make banner visibility configurable.
- [ ] **BANNER-005** Remove the draw handler cleanly on unregister.
- [ ] **BANNER-006** Avoid blocking viewport interaction.
- [ ] **BANNER-007** Verify behavior across common workspace layouts.

## 8.4 State Transitions

- [ ] **STATE-001** Support `READY`.
- [ ] **STATE-002** Support `PLANNING`.
- [ ] **STATE-003** Support `PLAN_REVIEW`.
- [ ] **STATE-004** Support `IMPLEMENTING`.
- [ ] **STATE-005** Support `VERIFYING_STATE`.
- [ ] **STATE-006** Support `CAPTURING_SCREENSHOT`.
- [ ] **STATE-007** Support `VISUAL_REVIEW`.
- [ ] **STATE-008** Support `FIXING`.
- [ ] **STATE-009** Support `EXPORTING`.
- [ ] **STATE-010** Support `COMPLETED`.
- [ ] **STATE-011** Support `FAILED`.
- [ ] **STATE-012** Support `DISCONNECTED`.
- [ ] **STATE-013** Define legal and illegal transitions.
- [ ] **STATE-014** Add transition tests outside Blender where possible.

### Phase 8 Exit Criteria

- [ ] The user can see connection and agent-work status inside Blender.
- [ ] Workflow updates appear without blocking Blender.
- [ ] Stale or disconnected sessions do not remain displayed as active.

---

# Phase 9 — Generic Agent Skill and User Documentation

## 9.1 Generic `SKILL.md`

- [ ] **SKILL-001** Create the generic bundled `SKILL.md`.
- [ ] **SKILL-002** Avoid product-specific agent metadata.
- [ ] **SKILL-003** Require `open_blender` first.
- [ ] **SKILL-004** Define plan format.
- [ ] **SKILL-005** Define plan reviewer inputs.
- [ ] **SKILL-006** Define plan reviewer PASS/FAIL output.
- [ ] **SKILL-007** Enforce three total plan attempts.
- [ ] **SKILL-008** Define implementation behavior.
- [ ] **SKILL-009** Require programmatic scene verification.
- [ ] **SKILL-010** Require screenshot capture.
- [ ] **SKILL-011** Define visual reviewer inputs.
- [ ] **SKILL-012** Define visual reviewer PASS/FAIL output.
- [ ] **SKILL-013** Enforce three total visual attempts.
- [ ] **SKILL-014** Define failed-verification preservation behavior.
- [ ] **SKILL-015** Require export after successful verification.
- [ ] **SKILL-016** Define final report structure.
- [ ] **SKILL-017** Test the instructions with at least one MCP-capable agent.

## 9.2 Fixed Reviewer Prompts

- [ ] **REVIEW-001** Create a plan-reviewer reference prompt.
- [ ] **REVIEW-002** Require strict structured PASS/FAIL output.
- [ ] **REVIEW-003** Create a visual-reviewer reference prompt.
- [ ] **REVIEW-004** Include user request, screenshot, scene summary, and acceptance criteria.
- [ ] **REVIEW-005** Require concrete fixes for visual failure.
- [ ] **REVIEW-006** Document that the agent product supplies sub-agent delegation.

## 9.3 Current Technical Documentation

- [ ] **DOCS-001** Create `docs/architecture.md`.
- [ ] **DOCS-002** Create `docs/ipc-protocol.md`.
- [ ] **DOCS-003** Create `docs/security.md`.
- [ ] **DOCS-004** Create `docs/development.md`.
- [ ] **DOCS-005** Update `docs/README.md` links when files exist.
- [ ] **DOCS-006** Document the external Python and Blender Python separation.
- [ ] **DOCS-007** Document Blender main-thread safety.
- [ ] **DOCS-008** Document runtime directory layout.
- [ ] **DOCS-009** Document logging locations and redaction rules.
- [ ] **DOCS-010** Document supported and unsupported environments.

## 9.4 Root README

- [ ] **README-001** Expand the project overview.
- [ ] **README-002** Explain the v0.1.0 status.
- [ ] **README-003** Document requirements.
- [ ] **README-004** Document installation with `uv`.
- [ ] **README-005** Document `agentic-blender init`.
- [ ] **README-006** Document generic MCP registration.
- [ ] **README-007** Document generic skill installation.
- [ ] **README-008** List the six v0.1.0 tools.
- [ ] **README-009** Document safety limitations.
- [ ] **README-010** Link to the PRD and technical docs.

### Phase 9 Exit Criteria

- [ ] A user can set up the product without source-code inspection.
- [ ] An MCP-capable agent can understand the required workflow from `SKILL.md`.
- [ ] Documentation accurately reflects the implementation.

---

# Phase 10 — Verification, Hardening, and Release

## 10.1 Unit Tests

- [ ] **TEST-001** Configuration tests.
- [ ] **TEST-002** Path tests.
- [ ] **TEST-003** Model validation tests.
- [ ] **TEST-004** Error serialization tests.
- [ ] **TEST-005** Blender version parsing tests.
- [ ] **TEST-006** Process discovery tests.
- [ ] **TEST-007** Atomic JSON tests.
- [ ] **TEST-008** Session tests.
- [ ] **TEST-009** Locking tests.
- [ ] **TEST-010** Tool schema tests.
- [ ] **TEST-011** CLI tests.

## 10.2 Integration Tests

- [ ] **ITEST-001** MCP server startup test.
- [ ] **ITEST-002** Fake bridge command-response test.
- [ ] **ITEST-003** Timeout test.
- [ ] **ITEST-004** Stale heartbeat test.
- [ ] **ITEST-005** Invalid session test.
- [ ] **ITEST-006** Duplicate command test.
- [ ] **ITEST-007** Output path validation test.
- [ ] **ITEST-008** Screenshot result packaging test.

## 10.3 Blender Smoke Tests

- [ ] **BTEST-001** Install extension into Blender 5.2.0 LTS.
- [ ] **BTEST-002** Enable extension.
- [ ] **BTEST-003** Confirm heartbeat.
- [ ] **BTEST-004** Execute a safe ping command.
- [ ] **BTEST-005** Open a new default project.
- [ ] **BTEST-006** Detect unsaved changes.
- [ ] **BTEST-007** Delete `Cube`.
- [ ] **BTEST-008** Add `Sphere`.
- [ ] **BTEST-009** Inspect the scene.
- [ ] **BTEST-010** Capture the Blender window.
- [ ] **BTEST-011** Save the `.blend` project.
- [ ] **BTEST-012** Reopen the exported project.
- [ ] **BTEST-013** Confirm the final scene after reopen.

## 10.4 Full Acceptance Test

- [ ] **E2E-001** Install Agentic Blender on a clean supported environment.
- [ ] **E2E-002** Run `agentic-blender init`.
- [ ] **E2E-003** Run `agentic-blender doctor`.
- [ ] **E2E-004** Register the MCP server using generic instructions.
- [ ] **E2E-005** Install or provide the generic `SKILL.md`.
- [ ] **E2E-006** Invoke `open_blender` with Blender closed.
- [ ] **E2E-007** Verify visible Blender launch.
- [ ] **E2E-008** Verify extension status UI.
- [ ] **E2E-009** Complete plan review within three attempts.
- [ ] **E2E-010** Delete the default cube.
- [ ] **E2E-011** Add a sphere.
- [ ] **E2E-012** Pass programmatic verification.
- [ ] **E2E-013** Capture a screenshot.
- [ ] **E2E-014** Pass visual review within three attempts.
- [ ] **E2E-015** Export the `.blend` file.
- [ ] **E2E-016** Reopen the `.blend` file.
- [ ] **E2E-017** Validate the final report.
- [ ] **E2E-018** Repeat `open_blender` while Blender is already connected.
- [ ] **E2E-019** Confirm no duplicate instance is created.
- [ ] **E2E-020** Confirm unsaved work protection.

## 10.5 Security Verification

- [ ] **SECTEST-001** Confirm no network listener is opened.
- [ ] **SECTEST-002** Confirm arbitrary command types are rejected.
- [ ] **SECTEST-003** Confirm invalid session tokens are rejected.
- [ ] **SECTEST-004** Confirm session secrets are not logged.
- [ ] **SECTEST-005** Confirm accidental output overwrite is rejected.
- [ ] **SECTEST-006** Confirm unsaved Blender work is not discarded silently.
- [ ] **SECTEST-007** Confirm unrelated files are not removed during uninstall.

## 10.6 Failure and Recovery Tests

- [ ] **FAIL-001** Blender executable missing.
- [ ] **FAIL-002** Unsupported Blender version.
- [ ] **FAIL-003** Blender startup timeout.
- [ ] **FAIL-004** Extension not installed.
- [ ] **FAIL-005** Extension disabled.
- [ ] **FAIL-006** Blender disconnects during a command.
- [ ] **FAIL-007** MCP server restarts.
- [ ] **FAIL-008** Stale heartbeat.
- [ ] **FAIL-009** Malformed IPC file.
- [ ] **FAIL-010** Read-only session directory.
- [ ] **FAIL-011** Invalid screenshot directory.
- [ ] **FAIL-012** Invalid export directory.
- [ ] **FAIL-013** Existing screenshot filename.
- [ ] **FAIL-014** Existing `.blend` filename.
- [ ] **FAIL-015** Visual review fails three times.
- [ ] **FAIL-016** Plan review fails three times.

## 10.7 Release Preparation

- [ ] **REL-001** Review every PRD requirement against implementation.
- [ ] **REL-002** Mark completed tasks accurately.
- [ ] **REL-003** Resolve or explicitly defer open implementation questions.
- [ ] **REL-004** Update accepted decision records.
- [ ] **REL-005** Update `CHANGELOG.md`.
- [ ] **REL-006** Verify package metadata.
- [ ] **REL-007** Build the Python distribution.
- [ ] **REL-008** Inspect wheel contents.
- [ ] **REL-009** Confirm extension and `SKILL.md` are included.
- [ ] **REL-010** Install the built artifact into a clean environment.
- [ ] **REL-011** Run the full acceptance test from the built artifact.
- [ ] **REL-012** Tag `v0.1.0` only after acceptance passes.

### Phase 10 Exit Criteria

- [ ] All release criteria in `PRD.md` are satisfied.
- [ ] The full sphere workflow passes on Blender 5.2.0 LTS.
- [ ] No critical or high-severity known issue remains.
- [ ] Documentation and packaged resources match the released implementation.

---

# 11. PRD Traceability

The following table maps major PRD areas to task groups.

| PRD Area | Primary Task Groups |
|---|---|
| Complete local setup | `REP-*`, `BLD-*`, `EXTINS-*`, `INIT-*` |
| Reuse visible Blender | `PROC-*`, `LAUNCH-*`, `OPEN-*` |
| Protect unsaved work | `OPEN-*`, `OPS-*`, `SECTEST-*` |
| Structured scene editing | `MCPTOOL-*`, `DEL-*`, `PRIM-*` |
| Programmatic verification | `INSP-*`, `E2E-*` |
| Screenshot capture | `WIN-*`, `SHOT-*` |
| Valid Blender export | `EXP-*`, `BTEST-*` |
| Extension workflow UI | `WFUI-*`, `PANEL-*`, `BANNER-*`, `STATE-*` |
| Reusable agent workflow | `SKILL-*`, `REVIEW-*` |
| Diagnostics | `DOC-*`, `STAT-*` |
| Local security model | `SES-*`, `BRG-*`, `SECTEST-*` |
| Testing and release | `TEST-*`, `ITEST-*`, `BTEST-*`, `E2E-*`, `REL-*` |

# 12. Known Dependencies Between Task Groups

```text
Shared models and paths
    ↓
Blender discovery + extension packaging
    ↓
Sessions + IPC + bridge
    ↓
CLI init/doctor + MCP adapter
    ↓
Scene tools
    ↓
Screenshot + export
    ↓
Workflow UI + generic skill
    ↓
End-to-end tests + release
```

Key constraints:

- MCP tools depend on shared models and the IPC client.
- Scene tools depend on a working extension bridge.
- `open_blender` depends on process discovery, extension registration, and session management.
- Screenshot capture depends on a verified Blender process and window identity.
- Extension status UI depends on a stable workflow status schema.
- The generic skill must be validated against the final tool names and schemas.

# 13. Deferred to Future Releases

The following work must not be added to v0.1.0 unless the PRD is intentionally revised:

- macOS or Linux support.
- Remote or network control.
- Multiple controlled Blender instances.
- Arbitrary Blender Python execution.
- Materials, textures, cameras, and lights.
- Advanced mesh operations.
- 3D house construction.
- Production rendering.
- Agent-product-specific integrations.
- Background-only Blender workflows.

# 14. Final Definition of Done

Agentic Blender v0.1.0 is complete when a new user on Windows 10/11 with Blender 5.2.0 LTS can:

1. Install Agentic Blender using `uv`.
2. Run `agentic-blender init`.
3. Confirm the setup using `agentic-blender doctor`.
4. Register the generic MCP server.
5. Provide the bundled generic `SKILL.md` to an MCP-capable agent.
6. Ask the agent to replace the default cube with a sphere.
7. Watch Blender open or be reused visibly.
8. See `Agent is working` and workflow status inside Blender.
9. Receive a programmatically verified scene.
10. Receive a screenshot that passes visual review.
11. Receive a valid `.blend` project that reopens in Blender 5.2.0 LTS.
12. Receive a clear final report containing status and artifact paths.

All of the above must occur without silently discarding unsaved work, creating unintended duplicate Blender instances, exposing arbitrary execution, or entering an infinite review loop.
