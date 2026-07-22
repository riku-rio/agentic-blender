# Decision 0004: Use MCP stdio as the Only Transport

## Status

Accepted

## Date

2026-07-22

## Context

Agentic Blender is a local tool launched by an MCP-capable agent. The v0.1.0 workflow does not require remote access, a persistent service, browser clients, or multiple network consumers.

A network transport would introduce port management, authentication, firewall behavior, service lifecycle, and a larger attack surface before the local workflow is proven.

## Decision

Use MCP over `stdio` as the only supported transport in v0.1.0.

The canonical MCP server identity is:

```text
agentic-blender
```

The canonical command form is:

```text
uv tool run agentic-blender mcp
```

The equivalent `uvx` shorthand may be documented:

```text
uvx agentic-blender mcp
```

The MCP process must reserve standard output for protocol messages. Human-readable logs must go to standard error or log files.

## Alternatives Considered

### Streamable HTTP

Rejected because v0.1.0 is local-only and does not need a network service. HTTP would add binding, authentication, origin, firewall, and lifecycle concerns.

### SSE

Rejected because it is unnecessary for a process launched directly by an MCP client and would add network complexity.

### WebSocket

Rejected because no browser or bidirectional network client requirement exists in v0.1.0.

### Raw TCP

Rejected because it would require a custom transport contract, port allocation, authentication, and additional security controls.

### Multiple Transports

Rejected because supporting multiple transports would expand the test matrix without improving the first release's acceptance workflow.

## Consequences

### Positive

- MCP clients can launch and stop the server as a child process.
- No listening network port is required.
- The local security model is simpler.
- Configuration needs only a command and arguments.

### Negative

- Remote Blender control is not supported.
- The server lifetime is generally tied to the MCP client process.
- Logs must never contaminate protocol output on stdout.

## Implementation Requirements

- `agentic-blender mcp` must start the stdio server.
- The server name must be `agentic-blender`.
- stdout must be protocol-only.
- Logs must use stderr or files.
- No HTTP, SSE, WebSocket, or TCP listener may be opened by v0.1.0.
- Transport-specific SDK usage must remain behind an adapter boundary where practical.
