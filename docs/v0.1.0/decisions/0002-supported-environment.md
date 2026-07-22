# Decision 0002: Support Windows and Blender 5.2.0 LTS First

## Status

Accepted

## Date

2026-07-22

## Context

Agentic Blender v0.1.0 depends on operating-system-specific behaviors including Blender executable discovery, running-process inspection, desktop window identification, DPI-aware screenshot capture, and interaction with a visible Blender GUI.

Supporting multiple operating systems in the first release would multiply the implementation and test surface before the core architecture is proven. The initial development and validation environment is Windows with Blender 5.2.0 LTS.

The external CLI and MCP server run outside Blender and therefore need an explicit Python support policy. Development also benefits from one pinned interpreter version for reproducibility.

## Decision

The official v0.1.0 environment is:

| Component | Supported Target |
|---|---|
| Operating system | Windows 10/11 x64 |
| Blender | Blender 5.2.0 LTS |
| External Python runtime | Python 3.10 or newer |
| Development Python | Python 3.11 |
| MCP transport | Local `stdio` |

Blender version handling follows this policy:

- Blender `5.2.0 LTS` is the official development and release-validation target.
- Later `5.2.x LTS` patch releases may be treated as supported only after the project smoke test passes on that version.
- Versions newer than the tested 5.2 LTS line must be reported as unverified or experimental.
- Versions older than 5.2.0 are unsupported in v0.1.0.

The Blender extension runs in Blender's embedded Python interpreter and does not use the project's external virtual environment.

## Alternatives Considered

### Support Windows, macOS, and Linux in v0.1.0

Rejected because process discovery, application launching, window capture, DPI behavior, installation locations, and extension management differ significantly across platforms. Supporting all three would delay validation of the core workflow.

### Support Any Recent Blender Version

Rejected because Blender API and extension-manifest compatibility can change between releases. An explicit version target makes failures reproducible and release criteria testable.

### Require Exactly Python 3.11 for Users

Rejected because supporting Python 3.10 and newer gives users reasonable flexibility while keeping Python 3.11 as the reproducible contributor environment.

### Use Blender's Python for the MCP Server

Rejected because the external MCP process needs independent dependency management, lifecycle control, and CLI execution. Blender's interpreter remains reserved for extension-side operations.

## Consequences

### Positive

- The release has a concrete and reproducible test matrix.
- Windows-specific screenshot and process behavior can be implemented thoroughly.
- Blender API behavior is anchored to one LTS release.
- Contributors use a consistent Python version while users retain limited flexibility.

### Negative

- macOS and Linux users are unsupported in v0.1.0.
- Newer Blender versions may work but cannot be advertised as supported without testing.
- Some external Python dependencies require Windows-specific conditional installation.

## Implementation Requirements

- `agentic-blender doctor` must report the operating system, architecture, Blender version, and support state.
- Package metadata must declare Python `>=3.10`.
- `.python-version` must pin Python 3.11 for development.
- CI must test supported external Python versions where practical.
- Blender smoke and end-to-end tests must run against Blender 5.2.0 LTS on Windows.
- Documentation must not imply support for macOS, Linux, or untested Blender versions.
