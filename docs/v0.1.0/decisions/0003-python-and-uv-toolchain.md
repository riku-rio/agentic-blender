# Decision 0003: Use Python and the uv Toolchain

## Status

Accepted

## Date

2026-07-22

## Context

Agentic Blender consists of an external CLI and MCP server plus a Blender extension. Blender exposes its automation API through Python, so using Python on both sides reduces language boundaries, duplicated models, packaging complexity, and contributor setup.

The external project also needs reproducible Python installation, dependency locking, virtual-environment management, command execution, and package builds. The project should use one coherent toolchain instead of combining several independent tools for these responsibilities.

## Decision

Use Python as the only implementation language for v0.1.0.

Use `uv` for:

- Python version management.
- Project initialization.
- Virtual environment management.
- Runtime and development dependency management.
- Dependency locking through `uv.lock`.
- Local command execution through `uv run`.
- Python CLI tool execution through `uv tool run` or the equivalent `uvx` shorthand.
- Building and publishing workflows.

Use `uv_build` as the Python build backend.

Use the following Python policy:

- External runtime: Python 3.10 or newer.
- Pinned contributor environment: Python 3.11.
- Blender extension: Blender 5.2.0 LTS embedded Python.

The Blender extension must not depend on the external uv-managed environment.

## Alternatives Considered

### Node.js and TypeScript

Rejected because Blender's native automation API is Python-based. A TypeScript MCP server would introduce a cross-language protocol and duplicated models without a v0.1.0 requirement that justifies the additional complexity.

### Rust

Rejected because the first release is dominated by Blender Python API operations, orchestration, JSON models, filesystem IPC, and CLI behavior rather than performance-sensitive native work. Rust would increase build and contributor complexity.

### C++

Rejected because no Blender core modification, native extension, or performance-critical component is required in v0.1.0. C++ would substantially increase build, packaging, and compatibility costs.

### Multiple Implementation Languages

Rejected because the foundation release benefits from one language, one type/model strategy, and one contributor workflow.

### pip, venv, setuptools, and Separate Locking Tools

Rejected as the primary workflow because `uv` provides the required responsibilities through one tool with a committed lockfile and reproducible command interface.

### Poetry, PDM, or Hatch

Not selected because `uv` covers the project's environment, dependency, tool-running, locking, and build requirements with a smaller operational surface for this project.

## Consequences

### Positive

- External and Blender-side code use the same language.
- Shared concepts can be represented consistently even though the runtimes remain separate.
- Contributor setup is concise and reproducible.
- `uv.lock` records exact external dependencies.
- The project avoids Node.js and native compiler prerequisites.

### Negative

- Blender-side modules cannot directly install or import the project's external third-party dependencies.
- The project must carefully separate code that runs externally from code that runs in Blender.
- Native performance optimizations would require a later decision if they become necessary.
- Contributors must install `uv` in addition to Blender.

## Implementation Requirements

- `pyproject.toml` must use `uv_build` as its build backend.
- `uv.lock` and `.python-version` must be committed.
- `src/agentic_blender/` must contain the external package.
- Blender extension code must be bundled as package resources but run independently inside Blender.
- Project documentation and CI commands must use `uv` rather than mixed package-management instructions.
- No Node.js, TypeScript, Rust, or C++ build system may be introduced in v0.1.0 without superseding this decision.
