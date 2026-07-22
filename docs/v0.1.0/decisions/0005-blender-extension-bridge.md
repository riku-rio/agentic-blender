# Decision 0005: Split the System Between an External Server and Blender Extension

## Status

Accepted

## Date

2026-07-22

## Context

The MCP server and CLI need normal external Python dependency management, process control, OS integration, and stdio communication with an agent. Blender scene operations, however, must execute inside Blender's embedded Python environment through `bpy`.

Importing or emulating `bpy` in the external Python environment would not provide safe control over the user's running Blender UI. Conversely, running the entire MCP server inside Blender would complicate process lifecycle, dependency installation, stdio ownership, and agent configuration.

Blender also requires UI and data operations to occur on its main thread. Background polling may detect commands, but it must not invoke `bpy` directly from an arbitrary worker thread.

## Decision

Split Agentic Blender into two cooperating components:

1. **External Python application**
   - CLI.
   - MCP stdio server.
   - Configuration and diagnostics.
   - Blender discovery and process management.
   - Session management and IPC client.
   - Windows screenshot capture.

2. **Blender Extension**
   - Runs inside Blender 5.2.0 LTS.
   - Registers the Blender process and heartbeat.
   - Polls for validated commands.
   - Executes allowlisted `bpy` operations.
   - Publishes results and workflow status.
   - Displays the Agentic Blender panel and viewport banner.

The extension must execute Blender API operations on Blender's main thread, using a Blender-safe scheduling mechanism such as `bpy.app.timers`.

The extension must have zero third-party runtime dependencies. It may use Blender-provided modules and the Python standard library only.

## Alternatives Considered

### External Python With pip `bpy`

Rejected because it does not safely control the intended visible Blender process and creates version and environment mismatch risks.

### Entire MCP Server Inside Blender

Rejected because MCP stdio lifecycle, external dependency management, agent configuration, and OS-level capture are better owned by a normal external process.

### Direct UI Automation Only

Rejected because simulated mouse and keyboard actions are fragile, context-sensitive, difficult to verify, and unnecessary for core Blender data operations.

### Third-Party Dependencies Inside the Extension

Rejected because Blender extension installation should not need a second package manager or modify Blender's embedded Python environment.

### Calling `bpy` From a Polling Thread

Rejected because Blender's API and UI state are not generally safe to manipulate from arbitrary threads.

## Consequences

### Positive

- Each runtime owns the responsibilities it handles best.
- Blender operations use the real embedded API in the visible application.
- External dependencies remain isolated from Blender.
- The extension can expose status directly in Blender.
- The architecture supports reusing an already-open Blender instance.

### Negative

- The project must define and maintain an IPC protocol.
- Models exist across two separate Python runtimes and cannot be imported blindly if they depend on third-party libraries.
- Installation must manage both a Python package and a Blender extension.
- Error reporting must cross the bridge reliably.

## Implementation Requirements

- External code must not import pip-installed `bpy` as a control mechanism.
- The extension must use no third-party packages.
- IPC schemas shared with the extension must be representable with standard JSON and standard-library code.
- All `bpy` mutations must run on Blender's main thread.
- Extension registration and unregistration must cleanly start and stop timers and UI handlers.
- The external server must treat missing or stale extension heartbeats as a disconnected Blender state.
