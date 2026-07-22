# Decision 0006: Use Per-Session File-Based IPC

## Status

Accepted

## Date

2026-07-22

## Context

The external MCP server and the Blender extension run in separate Python processes and environments. They need a local communication mechanism that is simple to inspect, debug, test, recover, and implement using only the Python standard library inside Blender.

The first release does not require high-throughput streaming or remote communication. Commands are relatively infrequent and interactive, such as opening a project, deleting an object, adding a primitive, inspecting a scene, saving a file, and updating workflow status.

## Decision

Use file-based JSON IPC in a unique directory for each active session.

The conceptual session layout is:

```text
session-root/
├── session.json
├── heartbeat.json
├── status.json
├── inbox/
│   └── <command-id>.json
└── outbox/
    └── <command-id>.json
```

Responsibilities:

- `session.json` stores protocol version, session identity, process association, timestamps, and non-secret metadata required for connection.
- `heartbeat.json` is periodically replaced by the Blender extension and identifies the connected Blender process, Blender version, extension version, and latest heartbeat time.
- `status.json` contains the current agent workflow status displayed by the Blender extension.
- `inbox/<command-id>.json` contains one validated command envelope for the Blender extension.
- `outbox/<command-id>.json` contains the matching success or structured failure response.

All writes must use an atomic lifecycle:

1. Write complete JSON to a temporary file in the destination directory.
2. Flush and close it.
3. Atomically replace or rename it to the final filename.

Commands and responses must include unique IDs, timestamps, protocol versions, session identity, and bounded expiry or timeout information.

Session authentication data must be unpredictable and must not be logged. Its exact storage and validation format will be defined in the IPC protocol and security documentation.

## Alternatives Considered

### Local TCP Socket

Rejected for v0.1.0 because it requires port lifecycle, binding policy, authentication, firewall considerations, and additional extension networking code.

### Unix Domain Socket or Windows Named Pipe

Not selected because the first release targets straightforward standard-library behavior and inspectability. Named pipes may be revisited for lower latency or stronger OS-level channel semantics.

### WebSocket

Rejected because the bridge is local and request-response oriented. A WebSocket server would add unnecessary dependencies or protocol code inside Blender.

### SQLite

Rejected because the command volume is low and the additional schema, locking, and database lifecycle are not needed for the foundation release.

### Shared Memory

Rejected because it is harder to inspect, debug, recover, and implement portably.

### Watching the Filesystem With a Third-Party Library

Rejected because the Blender extension must have zero third-party dependencies. Bounded timer polling is sufficient for v0.1.0.

## Consequences

### Positive

- IPC state is inspectable during development and diagnostics.
- Both runtimes can implement it with the standard library.
- Atomic file replacement avoids readers observing partial JSON.
- Session directories provide natural isolation and cleanup boundaries.
- Fake bridge and failure tests can be implemented without Blender.

### Negative

- Polling adds latency compared with sockets or pipes.
- Stale files and abandoned sessions require cleanup policies.
- Antivirus, sync software, or unusual filesystems may affect timing.
- Correct atomicity and duplicate-processing prevention require careful implementation.

## Future Migration

A future release may replace or supplement file IPC with Windows named pipes, local sockets, or another local transport if profiling demonstrates a real need.

Such a change is not committed for any specific release. The command and response model should remain transport-neutral enough to permit migration without redesigning MCP tool contracts.

## Implementation Requirements

- Create one isolated runtime directory per session.
- Use JSON-compatible schemas and UTF-8 encoding.
- Use atomic temporary-file replacement for every shared file.
- Process each command ID at most once.
- Match every response to its command ID.
- Detect malformed, expired, stale, duplicate, and unauthorized messages.
- Use bounded polling and bounded command timeouts.
- Clean expired sessions and messages without deleting active data.
- Document the exact schemas and lifecycle in `docs/ipc-protocol.md`.
