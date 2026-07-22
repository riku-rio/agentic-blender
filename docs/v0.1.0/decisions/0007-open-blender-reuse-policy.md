# Decision 0007: Reuse a Connected Blender Instance Safely

## Status

Accepted

## Date

2026-07-22

## Context

Agents may call `open_blender` more than once during a task, and users may already have Blender open before the MCP workflow begins.

Launching a new Blender process for every call creates duplicate windows, loses continuity, wastes resources, and can target the wrong project. Reusing a running process is desirable only when Agentic Blender can verify that its extension is connected to that exact process.

The workflow must also protect unsaved user work. Creating a new default project in an existing Blender instance is destructive when the current file has unsaved changes.

More than one connected Blender instance may exist in a future or unusual local setup, so the policy must avoid silently choosing an arbitrary process.

## Decision

`open_blender` is idempotent for the active Agentic Blender session.

The tool follows this order:

1. Discover live Blender registrations published by the Agentic Blender extension.
2. Remove stale registrations using process identity and heartbeat age.
3. If one eligible connected instance exists, reuse it.
4. If no connected instance exists and no blocking Blender condition exists, launch the configured Blender 5.2.0 LTS executable visibly and wait for its extension handshake.
5. Before creating a clean default project, inspect Blender's unsaved-change state.
6. If unsaved changes exist, stop with `UNSAVED_CHANGES` unless explicit user authorization to discard has been supplied through a destructive option.
7. Never let the agent infer or grant that authorization on the user's behalf.

If Blender is running but Agentic Blender cannot establish a verified extension connection to it, return `BLENDER_NOT_CONNECTED` with remediation guidance. Do not silently launch another Blender instance merely to bypass the disconnected process.

### Multiple Connected Instances

For v0.1.0, automatic reuse is allowed only when there is exactly one eligible connected Blender instance or when the session is already bound to a specific process.

If multiple eligible unbound instances exist, `open_blender` must return a structured ambiguity error and provide process identifiers and user-recognizable metadata. A later CLI or tool input may allow explicit instance selection, but arbitrary first-match selection is prohibited.

Once a session binds to a Blender process, later calls must reuse that process while it remains live and connected.

## Alternatives Considered

### Always Launch a New Instance

Rejected because repeated tool calls would create duplicate windows and would ignore an already-working extension connection.

### Reuse Any Running `blender.exe`

Rejected because process name alone does not prove that the correct extension is installed, enabled, connected, or associated with the active session.

### Automatically Discard Unsaved Work

Rejected because it can destroy user data and violates the project's safe-by-default principle.

### Automatically Save Unsaved Work to an Arbitrary Location

Rejected because the product cannot safely infer the user's desired filename, location, overwrite policy, or intent.

### Select the First Connected Instance

Rejected because process enumeration order is not a meaningful or safe selection policy.

### Launch a Second Instance When a Disconnected Instance Exists

Rejected for v0.1.0 because it can confuse the user, produce screenshots of the wrong window, and hide a broken installation or extension state.

## Consequences

### Positive

- Repeated `open_blender` calls do not create unintended duplicate processes.
- The agent operates only on a verified extension-enabled Blender instance.
- Unsaved user work is protected by default.
- Ambiguous multiple-instance situations fail visibly rather than targeting a random process.

### Negative

- A running Blender instance with a disabled or missing extension blocks automatic launch and requires user remediation.
- Users with multiple connected instances may need an explicit selection workflow.
- Reliable reuse depends on process metadata, heartbeats, and stale-session cleanup.

## Implementation Requirements

- Extension registrations must include Blender PID, executable identity, Blender version, extension version, and heartbeat time.
- `open_blender` must acquire a launch lock before deciding to start Blender.
- The active session must store its bound Blender process identity.
- Repeated calls must reuse the bound live process.
- Unsaved changes must be checked inside Blender before a new project is created.
- Discard authorization must be explicit and destructive by design.
- The tool must return whether the process was launched or reused.
- Tests must cover closed Blender, one connected instance, a disconnected running instance, unsaved changes, stale registration, repeated calls, and multiple connected instances.
