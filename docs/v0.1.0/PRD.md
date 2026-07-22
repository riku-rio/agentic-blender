# Agentic Blender v0.1.0 Product Requirements Document

## Document Status

- **Version:** v0.1.0
- **Status:** Draft
- **Date:** 2026-07-22
- **Target platform:** Windows 10/11 x64
- **Target Blender version:** Blender 4.5 LTS

## 1. Product Summary

Agentic Blender is an agent-agnostic Model Context Protocol server and Blender extension that allow AI agents to control a visible Blender application through a structured, inspectable, and verifiable workflow.

The first release establishes the complete product foundation rather than a temporary demonstration. The end-to-end acceptance scenario is intentionally small: remove Blender's default cube, add a sphere, verify the result, capture a screenshot, and save a valid Blender project.

The small modeling task must exercise the full system:

```text
Install
→ Initialize
→ Connect
→ Open or reuse Blender
→ Plan
→ Review the plan
→ Implement
→ Verify programmatically
→ Capture a screenshot
→ Review visually
→ Export
→ Report
```

## 2. Problem Statement

AI coding agents can call MCP tools, but Blender automation presents additional constraints:

- Blender operations must run inside Blender's embedded Python environment.
- The user should be able to watch the agent work in the normal Blender GUI.
- An already-open Blender instance should be reused instead of launching duplicate applications.
- Existing unsaved user work must not be destroyed.
- A successful tool response does not prove that the visual result is correct.
- Agents need a repeatable workflow for planning, implementation, verification, retries, and export.
- Installation and configuration must not depend on one specific agent product.

Agentic Blender v0.1.0 addresses these constraints with a local MCP server, a Blender extension, a visible workflow status UI, structured Blender tools, programmatic scene inspection, screenshot capture, visual review instructions, and safe project export.

## 3. Product Principles

### 3.1 Agent-Agnostic

The project must not require a product-specific integration for Codex, Claude Code, Cursor, or another agentic coding tool.

The product will provide:

- A standards-based MCP server over `stdio`.
- A canonical MCP server descriptor.
- A generic `SKILL.md` containing workflow instructions.
- CLI help that explains how to register the server and use the skill.

### 3.2 Visible by Default

Blender must run as a normal desktop application. The agent must not perform the primary workflow in Blender background mode.

The user should be able to observe:

- The Blender window.
- The current project state.
- The agent workflow state.
- The latest operation performed by the agent.

### 3.3 Safe by Default

The product must protect user work and avoid unnecessary execution capabilities.

In v0.1.0:

- Unsaved Blender work must not be discarded automatically.
- Arbitrary Python execution must not be exposed as an MCP tool.
- Modeling operations must be allowlisted and typed.
- The MCP server must communicate only with a locally installed Blender extension.
- Session communication must use per-session authentication data.

### 3.4 Verifiable

Completion requires more than successful command execution.

The workflow must support:

- Programmatic scene inspection.
- Screenshot capture of the Blender application.
- Visual review by an agent or sub-agent.
- A maximum retry count to prevent infinite loops.
- Verification that exported artifacts exist and are valid enough to reopen.

### 3.5 Small but Extensible

v0.1.0 must solve one small modeling scenario completely while establishing foundations that can support the v0.2.x 3D house workflow.

## 4. Goals

### G-001 — Complete Local Setup

A user can install Agentic Blender, run one initialization command, install and enable the Blender extension, validate the setup, and obtain generic MCP and skill instructions.

### G-002 — Reuse a Visible Blender Instance

The agent can open Blender when it is closed or reuse an already-open connected Blender instance without launching an unnecessary second instance.

### G-003 — Protect Unsaved Work

The product blocks creation of a new project when the target Blender instance contains unsaved changes, unless the user explicitly authorizes discarding them.

### G-004 — Perform Structured Scene Editing

The agent can remove the default cube and add a sphere using typed, allowlisted MCP tools.

### G-005 — Verify the Result

The agent can inspect the scene programmatically and capture a complete Blender application screenshot for visual review.

### G-006 — Export a Valid Blender Project

The agent can save the resulting project to a user-selected location as a normal `.blend` file.

### G-007 — Expose Workflow Status in Blender

The Blender extension displays that an agent is working and shows the current workflow phase, task summary, attempt number, connection status, and latest action when available.

### G-008 — Provide a Reusable Agent Workflow

The bundled generic `SKILL.md` describes the Plan → Review → Implement → Verify → Export workflow, including bounded retries and final reporting requirements.

### G-009 — Provide Diagnostics

The CLI can identify common installation, Blender, extension, connection, filesystem, and screenshot problems and provide actionable remediation.

## 5. Non-Goals

The following are explicitly out of scope for v0.1.0:

- Building a 3D house.
- Advanced mesh editing.
- Materials and textures.
- Lighting configuration.
- Camera configuration.
- Rendering a production image.
- Geometry Nodes.
- Animation.
- Sculpting.
- Arbitrary Python execution.
- Remote Blender control over the network.
- HTTP, SSE, WebSocket, or TCP MCP transports.
- macOS support.
- Linux support.
- Multiple simultaneously controlled Blender sessions.
- Automatic integrations for individual agent products.
- Cloud-hosted services.
- Docker-based execution.

These capabilities may be considered in later releases.

## 6. Target Users

### 6.1 Primary User

A developer or technical creator who uses an MCP-capable AI agent and wants the agent to operate Blender locally while the work remains visible and reviewable.

### 6.2 Secondary User

A contributor developing new Agentic Blender tools, extension capabilities, workflow rules, or platform support.

## 7. Primary User Journey

### 7.1 Installation and Initialization

1. The user installs Agentic Blender using `uv` tooling.
2. The user runs:

   ```powershell
   agentic-blender init
   ```

3. The CLI detects supported Blender installations.
4. If more than one supported installation exists, the user can select the target installation.
5. The CLI installs and enables the Agentic Blender extension.
6. The CLI creates required configuration, runtime, session, and log directories.
7. The CLI performs a connection test.
8. The CLI prints generic MCP server registration information.
9. The CLI explains how to obtain and install the bundled `SKILL.md`.
10. The CLI runs or recommends `agentic-blender doctor`.

### 7.2 Agent Execution

1. The agent invokes `open_blender`.
2. Agentic Blender opens Blender or reuses the connected instance.
3. A clean default project becomes active, unless unsaved changes block the operation.
4. The Blender extension displays the active agent task and workflow status.
5. The agent creates a plan with testable acceptance criteria.
6. A reviewer sub-agent evaluates the plan.
7. The agent revises the plan when required, up to three total plan attempts.
8. The agent calls `delete_object` for `Cube`.
9. The agent calls `add_primitive` with `sphere`.
10. The agent calls `inspect_scene` and checks the expected state.
11. The agent calls `screenshot`.
12. A reviewer sub-agent evaluates the screenshot and scene summary.
13. The agent fixes any identified problem and repeats verification, up to three visual verification attempts.
14. The agent calls `export`.
15. The agent provides a final report with status, actions, verification results, attempts, and artifact paths.

## 8. Functional Requirements

## 8.1 CLI Requirements

### CLI-001 — Primary Command

The installed application must provide the command:

```text
agentic-blender
```

### CLI-002 — Initialization

The CLI must provide:

```powershell
agentic-blender init
```

`init` must:

- Detect supported Blender installations.
- Allow target selection when necessary.
- Install the bundled Blender extension.
- Enable the extension.
- Create application directories.
- Create or update local configuration.
- Validate the extension installation.
- Attempt a bridge handshake.
- Print generic MCP registration instructions.
- Print generic skill installation instructions.

### CLI-003 — Diagnostics

The CLI must provide:

```powershell
agentic-blender doctor
```

`doctor` must inspect at least:

- Supported Python runtime.
- Agentic Blender installation.
- Blender executable discovery.
- Blender version compatibility.
- Extension installation.
- Extension enablement.
- Runtime directory access.
- Session directory access.
- Bridge connectivity when Blender is running.
- Screenshot backend availability.
- Ability to execute a safe test command when possible.

Failures must include an actionable explanation or suggested fix.

### CLI-004 — Status

The CLI must provide:

```powershell
agentic-blender status
```

The command must report:

- Configured Blender installation.
- Whether Blender is running.
- Whether the extension is connected.
- Active session information, if any.
- Current workflow state, if any.
- Last heartbeat time.

### CLI-005 — MCP Server

The CLI must provide:

```powershell
agentic-blender mcp
```

This command must start the local MCP server using `stdio` transport.

A separate console entry point may also be provided, but both entry points must execute the same server implementation.

### CLI-006 — Help

The CLI must provide:

```powershell
agentic-blender help
```

Help must explain:

- What Agentic Blender does.
- Installation and initialization.
- The canonical MCP server name.
- The MCP transport, command, and arguments.
- How to obtain the generic `SKILL.md`.
- The available MCP tools.
- The expected agent workflow.
- Diagnostic and uninstall commands.

The help system may provide focused topics such as:

```powershell
agentic-blender help setup
agentic-blender help mcp
agentic-blender help skill
agentic-blender help tools
agentic-blender help workflow
```

### CLI-007 — Skill Output

The CLI must provide a way to print or copy the bundled generic `SKILL.md` without requiring an integration for a specific agent product.

A supported interface may include:

```powershell
agentic-blender help skill --print
agentic-blender help skill --output .\SKILL.md
```

### CLI-008 — Uninstall

The CLI must provide:

```powershell
agentic-blender uninstall
```

The command must support removing the Blender extension and Agentic Blender-managed runtime files without deleting unrelated Blender projects or user content.

## 8.2 Blender Extension Requirements

### EXT-001 — Installation

The extension must be bundled with the Agentic Blender Python package and installed through `agentic-blender init`.

### EXT-002 — Zero Third-Party Runtime Dependencies

The extension must run using Blender-provided modules and the Python standard library only.

### EXT-003 — Bridge Registration

When enabled, the extension must register the running Blender instance with Agentic Blender and maintain a heartbeat while Blender remains available.

### EXT-004 — Main-Thread Execution

All Blender API operations must execute through a Blender-safe main-thread mechanism.

Long-running background threads must not call `bpy` directly.

### EXT-005 — Workflow Panel

The extension must expose an `Agentic Blender` panel in the 3D Viewport sidebar.

The panel must display, when available:

- Connection status.
- Agent working state.
- Task summary.
- Workflow phase.
- Current step.
- Attempt number and maximum attempts.
- Last completed action.
- Failure reason.

### EXT-006 — Viewport Banner

The extension must support a lightweight viewport banner showing that the agent is working and the current step.

The banner must be user-configurable and must not permanently obstruct normal Blender usage.

### EXT-007 — Workflow States

The extension and runtime must support displaying at least these states:

```text
READY
PLANNING
PLAN_REVIEW
IMPLEMENTING
VERIFYING_STATE
CAPTURING_SCREENSHOT
VISUAL_REVIEW
FIXING
EXPORTING
COMPLETED
FAILED
DISCONNECTED
```

The mechanism used to update workflow states must remain agent-agnostic.

### EXT-008 — Reconnection

The extension must recover from MCP server restarts or stale sessions without requiring Blender to be reinstalled.

### EXT-009 — Safe Error Handling

Extension errors must be written to Agentic Blender logs and returned as structured failures when they are related to an active command.

An extension error must not silently report success.

## 8.3 MCP Server Requirements

### MCP-001 — Transport

The MCP server must use `stdio` transport in v0.1.0.

### MCP-002 — Canonical Server Identity

The canonical server name must be:

```text
agentic-blender
```

### MCP-003 — Generic Server Descriptor

The product must document a generic descriptor equivalent to:

```json
{
  "name": "agentic-blender",
  "transport": "stdio",
  "command": "uv",
  "args": ["tool", "run", "agentic-blender", "mcp"]
}
```

The documentation may also show the equivalent `uvx` shorthand when available.

### MCP-004 — Structured Inputs and Outputs

All tools must use typed input parameters and structured responses.

Tool failures must include:

- A stable error code.
- A human-readable message.
- Relevant context.
- A suggested action when one is available.

### MCP-005 — Local Operation

The MCP server must control only local Blender installations in v0.1.0.

### MCP-006 — Session Isolation

Each active run must use a unique session identifier and unpredictable session authentication data.

### MCP-007 — Timeouts

Commands must have bounded timeouts and must fail clearly when Blender is unresponsive, disconnected, or unable to complete an operation.

### MCP-008 — No Arbitrary Code Tool

The MCP server must not expose a tool that executes arbitrary Python code inside or outside Blender.

## 8.4 MCP Tool Requirements

v0.1.0 must expose these user-facing tools:

```text
open_blender
delete_object
add_primitive
inspect_scene
screenshot
export
```

Internal protocol operations do not need to be exposed as user-facing modeling tools.

### TOOL-001 — `open_blender`

Purpose: make a clean, connected Blender project ready for agent work.

Required behavior:

- If Blender is not running, launch it as a visible desktop application.
- Do not use Blender background mode for the primary workflow.
- If a connected Blender instance is already running, reuse it.
- Do not launch a duplicate Blender instance merely because the tool was called again.
- Create a new default project in the reused or newly launched instance.
- Focus or restore the Blender window when practical.
- Wait for a valid extension handshake before reporting readiness.
- Return process, session, connection, reuse, project, and scene summary information.

Unsaved work behavior:

- Detect unsaved changes in the selected Blender instance.
- Block creation of a new project by default when unsaved changes exist.
- Return a stable `UNSAVED_CHANGES` error.
- Require explicit user authorization before discarding unsaved work.
- The agent must not independently authorize destructive discard behavior.

Disconnected instance behavior:

- If Blender is running but no usable Agentic Blender extension connection exists, do not silently control it.
- Do not automatically launch a second instance unless a future explicit policy allows it.
- Return a stable `BLENDER_NOT_CONNECTED` error with remediation guidance.

### TOOL-002 — `delete_object`

Purpose: remove a named object from the active Blender scene.

Required inputs:

- Object name.
- Whether absence should be treated as an error.

Required behavior:

- Delete the object by data identity or name rather than relying only on current UI selection.
- Return the deleted object name and updated scene summary.
- Return a stable not-found error when required.

### TOOL-003 — `add_primitive`

Purpose: add a supported mesh primitive using one general tool.

Required base inputs:

- Primitive type.
- Optional object name.
- Location.
- Rotation.
- Scale.
- Size.

Supported v0.1.0 primitive types must include at least:

```text
cube
sphere
icosphere
cylinder
cone
torus
plane
circle
triangle
square
```

Convenience behavior:

- `sphere` may map internally to Blender's UV Sphere implementation.
- `square` may map internally to a plane.
- `triangle` may map internally to a three-vertex filled mesh.

The public tool must not expose implementation-specific naming such as `add_uv_sphere` for the standard sphere case.

The tool must return:

- Final object name.
- Blender object type.
- Primitive type requested.
- Transform information.
- Dimensions when available.

### TOOL-004 — `inspect_scene`

Purpose: provide machine-verifiable information about the current Blender scene.

The result must include at least:

- All relevant object names.
- Object types.
- Object transforms.
- Object dimensions when available.
- Active object.
- Mesh count.
- Current project path.
- Unsaved-change state.

For the v0.1.0 acceptance scenario, the response must allow the agent to verify that:

- `Cube` does not exist.
- `Sphere` exists.
- `Sphere` is a mesh.
- `Sphere` is at the expected location.

### TOOL-005 — `screenshot`

Purpose: capture the complete Blender application in the state left by the agent.

Required inputs:

- Output directory.
- Optional filename.
- Capture mode, with full Blender window as the required v0.1.0 mode.

Required behavior:

- Capture the correct Blender window associated with the active session.
- Support Windows display scaling and multiple-monitor coordinates where practical.
- Restore the window if minimized when safe and practical.
- Save a PNG file to the requested directory.
- Generate a timestamp-based filename when no filename is provided.
- Avoid overwriting an existing file unless explicitly allowed.
- Validate that the resulting PNG can be opened.
- Return the file path, dimensions, capture mode, timestamp, and image content or a form usable by an MCP client for visual review.

Filename generation must include enough timestamp precision to avoid accidental collisions during normal use.

### TOOL-006 — `export`

Purpose: save the active Blender project as a normal `.blend` file.

Required inputs:

- Output directory.
- Optional filename.
- Overwrite policy.

Required behavior:

- Generate a timestamp-based filename when no filename is provided.
- Ensure the output filename uses the `.blend` extension.
- Refuse accidental overwrite by default.
- Save using Blender's normal project-saving behavior.
- Verify that the resulting file exists and has non-zero size.
- Return the final path, size, scene summary, and verification status.

The exported file must be reopenable in the supported Blender version.

## 8.5 Agent Workflow Requirements

### WF-001 — Open First

The generic skill must instruct the agent to call `open_blender` before planning or scene-editing operations.

No scene-editing tool may be used before Blender readiness is confirmed.

### WF-002 — Plan

The agent must create a concise plan containing:

- Goal.
- Ordered implementation steps.
- Programmatic acceptance criteria.
- Visual acceptance criteria.
- Expected artifacts.

### WF-003 — Plan Review

A reviewer sub-agent must evaluate:

- The user request.
- The proposed plan.
- Available tools.
- Acceptance criteria.
- Safety constraints.

The reviewer must return either:

```text
PASS
```

or:

```text
FAIL with reason and required changes
```

The workflow must allow no more than three total plan attempts.

After three failed plan attempts, the task must stop and report the failure instead of entering an infinite loop.

### WF-004 — Implementation

After plan approval, the agent may call the necessary scene-editing tools.

For the v0.1.0 acceptance scenario, the normal sequence is:

```text
delete_object(name="Cube")
add_primitive(primitive_type="sphere", name="Sphere")
inspect_scene()
```

### WF-005 — Programmatic Verification

The agent must compare `inspect_scene` results with the plan's acceptance criteria before visual verification.

A known programmatic mismatch must not be ignored merely because the screenshot appears acceptable.

### WF-006 — Screenshot and Visual Review

After implementation and programmatic inspection, the agent must call `screenshot` and delegate review of the image.

The visual reviewer must receive:

- The original user request.
- The screenshot.
- The programmatic scene summary.
- The acceptance criteria.
- A fixed review instruction.

The reviewer must return either:

```text
PASS
```

or:

```text
FAIL with reason and concrete fixes
```

### WF-007 — Bounded Visual Fix Loop

When visual review fails, the agent must:

1. Apply the required fix.
2. Re-run relevant programmatic inspection.
3. Capture a new screenshot.
4. Re-run visual review.

The workflow must allow no more than three total visual review attempts.

After the third failure:

- The workflow must stop retrying.
- The work may be saved as an unverified result when safe.
- The final report must clearly state that visual verification failed.
- The task must not be reported as successful.

### WF-008 — Export After Verification

A successful workflow must call `export` only after required programmatic and visual verification passes.

A failed workflow may preserve work for debugging, but the result must be explicitly marked unverified.

### WF-009 — Final Report

The final report must include:

- Overall status.
- Summary of actions.
- Programmatic verification result.
- Visual verification result.
- Plan attempt count.
- Visual review attempt count.
- Screenshot path.
- Blender file path.
- Final scene summary.
- Any warnings, limitations, or unresolved failures.

## 9. Non-Functional Requirements

### NFR-001 — Supported Runtime

The external MCP server and CLI must support Python 3.10 or newer.

Development should use a pinned Python 3.11 environment unless a later decision changes it.

### NFR-002 — Package Management

The project must use `uv` for Python version management, dependency management, locking, execution, and packaging workflows.

### NFR-003 — Blender Compatibility

v0.1.0 officially supports Blender 4.5 LTS on Windows 10/11 x64.

Other Blender versions or operating systems must not be advertised as supported until tested and documented.

### NFR-004 — Reliability

The system must handle:

- Blender startup timeout.
- Extension connection timeout.
- Stale heartbeat.
- Blender process termination.
- Missing runtime directories.
- Unwritable output directories.
- Screenshot failures.
- Export failures.
- Malformed or stale IPC messages.

### NFR-005 — Observability

The product must create local logs sufficient to diagnose:

- CLI initialization.
- Blender discovery.
- Extension installation.
- Session creation.
- Command dispatch.
- Command completion or failure.
- Screenshot capture.
- Export.
- Heartbeat and disconnection events.

Secrets and session authentication data must not be written to logs in plain text.

### NFR-006 — Deterministic Errors

Common failures must use stable error codes so agents and tests can distinguish failure classes.

Required initial codes include at least:

```text
BLENDER_NOT_FOUND
BLENDER_UNSUPPORTED_VERSION
BLENDER_NOT_CONNECTED
BLENDER_START_TIMEOUT
BLENDER_DISCONNECTED
UNSAVED_CHANGES
OBJECT_NOT_FOUND
UNSUPPORTED_PRIMITIVE
INVALID_OUTPUT_PATH
OUTPUT_ALREADY_EXISTS
SCREENSHOT_FAILED
EXPORT_FAILED
COMMAND_TIMEOUT
INVALID_SESSION
```

### NFR-007 — Documentation

The repository must contain:

- Current architecture documentation.
- Current IPC protocol documentation.
- Current security documentation.
- Current development documentation.
- Versioned PRD.
- Versioned task list.
- Versioned decision records.

### NFR-008 — Testing

The release must include:

- Unit tests for core models and validation.
- Unit tests for path and configuration handling.
- IPC tests.
- Session and timeout tests.
- CLI tests where practical.
- Windows screenshot tests where practical.
- Blender extension tests or scripted smoke tests.
- A complete end-to-end sphere workflow smoke test.

### NFR-009 — No Hidden Destructive Behavior

No command may silently discard unsaved Blender data, overwrite an existing output artifact, or target an unverified Blender instance.

### NFR-010 — Performance

The product is interactive rather than real-time.

Reasonable local targets are:

- Normal bridge command dispatch should begin within one second while Blender is responsive.
- Heartbeat loss should be detected within a bounded interval.
- CLI commands must not wait indefinitely.
- Screenshot and export operations must provide bounded timeouts.

Exact performance thresholds may be refined during implementation and recorded in decision or test documentation.

## 10. Data and Artifact Requirements

### 10.1 Configuration

Configuration must support at least:

- Blender executable path.
- Selected Blender version.
- Application data paths.
- Session paths.
- Log paths.
- Screenshot defaults.
- Timeout defaults.
- Extension UI preferences where appropriate.

### 10.2 Session Data

Each session must have isolated runtime data for:

- Session identity.
- Authentication token or equivalent secret.
- Blender process identity.
- Heartbeat.
- Workflow status.
- Commands.
- Responses.
- Timestamps.
- Failure details.

### 10.3 Generated Artifacts

The primary v0.1.0 workflow generates:

- One or more PNG screenshots.
- One `.blend` project.
- Local diagnostic logs.

User-selected screenshot and project output paths must be respected.

## 11. Security Requirements

### SEC-001 — Local-Only Control

The extension bridge and MCP server must not expose a network-accessible control endpoint in v0.1.0.

### SEC-002 — Session Authentication

Commands must be associated with the active session and validated using unpredictable session authentication data or an equivalent mechanism.

### SEC-003 — Command Allowlist

The extension must execute only known command types with validated parameters.

### SEC-004 — Path Validation

Screenshot and export paths must be validated before use.

The product must reject invalid, inaccessible, or unsafe paths with structured errors.

### SEC-005 — No Arbitrary Execution

The product must not provide arbitrary shell, Python, or Blender script execution through MCP in v0.1.0.

### SEC-006 — User Data Protection

Unsaved Blender projects and unrelated files must not be deleted or overwritten without explicit user authorization.

## 12. UX Requirements

### UX-001 — Clear Setup Feedback

`init` and `doctor` must use clear success, warning, and failure messages.

### UX-002 — Actionable Failures

Errors must state:

- What failed.
- Why it likely failed.
- What the user or agent should do next.

### UX-003 — Visible Agent State

While an active task is running, the Blender extension must make it clear that the scene is being controlled by an agent.

### UX-004 — Non-Intrusive UI

The extension panel and viewport banner must not prevent normal user interaction with Blender.

### UX-005 — Artifact Discoverability

Tool responses and final reports must provide absolute artifact paths.

## 13. Acceptance Scenario

The primary acceptance test begins with Agentic Blender installed and Blender 4.5 LTS available.

### User Request

```text
Remove the default cube and replace it with a sphere. Save a screenshot and the Blender project in the requested output directory.
```

### Required Result

1. `agentic-blender init` successfully installs and enables the extension.
2. `agentic-blender doctor` reports a usable installation.
3. The agent can start the MCP server through the documented generic configuration.
4. `open_blender` opens a visible Blender instance or reuses the connected instance.
5. A clean default project becomes active.
6. The extension shows that the agent is working.
7. The plan review passes within three attempts.
8. `Cube` is deleted.
9. A mesh object named `Sphere` is added at the expected location.
10. `inspect_scene` confirms the required state.
11. `screenshot` creates a readable PNG of the Blender application.
12. Visual review passes within three attempts.
13. `export` creates a non-empty `.blend` file.
14. The `.blend` file reopens successfully in Blender 4.5 LTS.
15. The final report includes verification results and artifact paths.

## 14. Release Criteria

v0.1.0 is ready for release only when all of the following are true:

- All required CLI commands exist and have usable help output.
- Extension installation through `init` works on a clean supported Windows environment.
- The extension shows connection and workflow status.
- An already-open connected Blender instance is reused.
- Unsaved changes are protected by default.
- All six required MCP tools are implemented.
- Tool inputs and outputs are structured and validated.
- Common failures return stable error codes.
- The complete acceptance scenario passes.
- The exported `.blend` file reopens successfully.
- The screenshot correctly represents the active Blender window.
- The generic `SKILL.md` contains the bounded review workflow.
- `doctor` identifies common setup failures.
- Required unit, integration, and smoke tests pass.
- Security documentation describes the local trust model and known limitations.
- Architecture and IPC documentation match the implementation.
- `docs/v0.1.0/TASKS.md` reflects completed release work.
- All accepted v0.1.0 engineering decisions are recorded in `docs/v0.1.0/decisions/`.

## 15. Success Metrics

Because v0.1.0 is a foundation release, success is measured by reliability rather than adoption volume.

Initial success metrics are:

- The full sphere workflow completes successfully on a clean supported environment.
- Repeated `open_blender` calls do not create unintended duplicate Blender instances.
- Unsaved user work is never silently discarded in tests.
- The workflow cannot enter an unbounded plan or visual review loop.
- Every successful run produces both a screenshot and a reopenable `.blend` file.
- Common setup failures can be diagnosed through `agentic-blender doctor` without manually inspecting source code.

## 16. Future Direction

The v0.2.x release line will build on the v0.1.0 foundation and expand the modeling toolset for a simple 3D house workflow.

Potential v0.2.x areas include:

- Object transforms and dimensions.
- Duplication and collection management.
- Extrude, inset, bevel, join, and boolean operations.
- Modifiers.
- Materials and colors.
- Lights and cameras.
- Preview rendering.
- More detailed visual acceptance criteria.

These items are not commitments for v0.1.0 and must be specified in the relevant future PRD.

## 17. Open Implementation Questions

The following details must be resolved through v0.1.0 decision records before implementation is considered stable:

- Exact IPC message schema and atomic file lifecycle.
- Exact mechanism for publishing planning and review workflow states to the extension without coupling to one agent product.
- Exact extension packaging and enabling procedure for Blender 4.5 LTS.
- Exact Blender instance selection policy when multiple connected instances exist.
- Exact timeout and heartbeat intervals.
- Exact screenshot behavior for minimized, obscured, DPI-scaled, and multi-monitor windows.
- Exact policy for preserving an unverified result after the final visual review failure.
- Exact CLI interface for printing or copying `SKILL.md`.

Each resolved question should be documented in `docs/v0.1.0/decisions/` and reflected in `TASKS.md`.
