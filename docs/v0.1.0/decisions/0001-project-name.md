# Decision 0001: Use Agentic Blender as the Project Name

## Status

Accepted

## Date

2026-07-22

## Context

The project needs one stable identity across its GitHub repository, Python distribution, command-line interface, MCP server, documentation, and future release artifacts.

The name must communicate that the project enables agent-driven Blender workflows while remaining distinct from existing projects that use generic names such as `blender-mcp`.

Python packaging also distinguishes between distribution names, which commonly use hyphens, and import package names, which must use valid Python identifiers.

## Decision

Use the following canonical names:

| Surface | Name |
|---|---|
| Project | Agentic Blender |
| GitHub repository | `agentic-blender` |
| Python distribution | `agentic-blender` |
| Primary CLI command | `agentic-blender` |
| MCP server identity | `agentic-blender` |
| Python import package | `agentic_blender` |

Public documentation should use **Agentic Blender** when referring to the product and `agentic-blender` when referring to a repository, package, command, server identifier, or filesystem-compatible slug.

Python code must import the package as:

```python
import agentic_blender
```

## Alternatives Considered

### `blender-mcp`

Rejected because it is overly generic, does not distinguish this project's workflow-oriented design, and risks confusion with existing Blender MCP projects and package names.

### `blender-agent`

Rejected because it can imply that the project contains or hosts the AI agent itself. Agentic Blender provides tools and workflow instructions to external agents; it is not an agent runtime.

### `agentic_blender` for Every Surface

Rejected for user-facing package and command names because hyphenated names are more conventional and readable for Python distributions and CLI commands. The underscore form is retained only where Python identifier rules require it.

### A Product-Specific Name

Names tied to Codex, Claude, Cursor, or another agent product were rejected because the project is intentionally agent-agnostic.

## Consequences

### Positive

- One recognizable identity is used across the project.
- The name communicates both agentic operation and Blender integration.
- The project avoids coupling its brand to one MCP client or agent product.
- The Python import name follows normal Python identifier rules.

### Negative

- The name does not explicitly contain `MCP`, so the README and package description must clearly state that Agentic Blender exposes an MCP server.
- Contributors must remember the intentional hyphen-to-underscore distinction between distribution and import names.

## Implementation Requirements

- Package metadata must use `name = "agentic-blender"`.
- Source code must live under `src/agentic_blender/`.
- Console entry points must begin with `agentic-blender`.
- The MCP implementation name must be `agentic-blender`.
- Documentation and examples must not introduce competing canonical names.
