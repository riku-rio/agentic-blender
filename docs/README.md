# Agentic Blender Documentation

This directory contains the product, architecture, development, security, protocol, and release-specific documentation for Agentic Blender.

Agentic Blender is an agent-agnostic MCP server and Blender extension that allow AI agents to control a visible Blender application through a structured, inspectable, and verifiable workflow.

## Documentation Structure

The documentation is split into two categories:

1. **Current technical documentation** describes how the project works today.
2. **Versioned documentation** preserves the product scope, implementation plan, and decisions for each release.

## Current Technical Documentation

These documents represent the current state of the project and may evolve as the implementation changes:

- [Architecture](./architecture.md)
- [IPC Protocol](./ipc-protocol.md)
- [Security](./security.md)
- [Development Guide](./development.md)

## Versioned Documentation

Each planned or released version has its own directory:

```text
docs/
└── vX.Y.Z/
    ├── PRD.md
    ├── TASKS.md
    └── decisions/
        ├── 0001-example-decision.md
        └── 0002-another-decision.md
```

Each version directory contains:

- **`PRD.md`** — product requirements, goals, non-goals, supported workflows, acceptance criteria, and release criteria.
- **`TASKS.md`** — implementation tasks derived from the PRD.
- **`decisions/`** — decision records explaining important product and engineering choices, alternatives considered, and consequences.

Versioned documentation is a historical record. After a version is released, its documentation should not be rewritten to match a newer implementation. Later changes should be documented in the directory for the release that introduces them.

## Current Development Version

### v0.1.0 — Foundation

The first release establishes the complete Agentic Blender workflow and infrastructure.

- [Product Requirements](./v0.1.0/PRD.md)
- [Implementation Tasks](./v0.1.0/TASKS.md)
- [Decision Records](./v0.1.0/decisions/)

The primary end-to-end acceptance scenario for v0.1.0 is:

1. Initialize Agentic Blender and install its Blender extension.
2. Open Blender, or reuse an already connected Blender instance.
3. Create a clean default project.
4. Remove the default cube.
5. Add a sphere.
6. Inspect and verify the scene programmatically.
7. Capture a screenshot of the Blender application.
8. Perform visual verification.
9. Save a valid `.blend` file.
10. Report the actions, verification results, and generated artifacts.

## Planned Release Direction

### v0.1.x — Foundation Stabilization

Patch releases will focus on reliability, diagnostics, compatibility, tests, documentation, and fixes without substantially expanding the modeling toolset.

### v0.2.x — 3D House Workflow

The v0.2 release line will expand Blender modeling and scene-management tools, with a simple 3D house as the primary end-to-end acceptance scenario.

## Decision Record Format

Decision records use the following filename format:

```text
NNNN-short-decision-title.md
```

Each record should contain:

- Status
- Date
- Context
- Decision
- Alternatives considered
- Positive consequences
- Negative consequences
- Related decisions, when applicable

Supported decision statuses are:

- `Proposed`
- `Accepted`
- `Rejected`
- `Deprecated`
- `Superseded`

Decision numbering starts at `0001` within each version directory.

## Patch Release Documentation

Patch releases use delta documentation rather than copying the complete previous PRD.

For example, `docs/v0.1.1/PRD.md` should describe only what changes relative to v0.1.0, including:

- Base version
- Objective
- Changes
- Non-goals
- Acceptance criteria
- Release criteria

## Documentation Principles

All project documentation should follow these principles:

- Write in clear technical English.
- Record why a decision was made, not only what was selected.
- Keep requirements testable and implementation tasks actionable.
- Separate current technical truth from historical release records.
- Prefer explicit constraints over implied behavior.
- Link related requirements, tasks, and decisions when practical.
- Update versioned documentation before or alongside the implementation it governs.

## Contributing to Documentation

When proposing a meaningful product or engineering change:

1. Update the active version's PRD if the product scope changes.
2. Update the active version's task list if implementation work changes.
3. Add a decision record when the change introduces an important tradeoff or replaces an earlier decision.
4. Update current technical documentation once the implementation becomes the project's current behavior.
