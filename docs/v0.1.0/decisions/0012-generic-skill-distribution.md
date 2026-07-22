# Decision 0012: Distribute One Generic Agent Skill

## Status

Accepted

## Date

2026-07-22

## Context

Agentic Blender should work with any MCP-capable agent that can consume reusable instructions. Different agent products use different configuration directories, metadata formats, and conventions for skills or instruction files.

Maintaining separate integrations for Codex, Claude Code, Cursor, or other products would couple the project to vendor-specific behavior and expand the support surface before the core product is stable.

The project still needs to distribute a canonical workflow that tells agents how to use the MCP tools safely and consistently.

## Decision

Distribute one generic file named:

```text
SKILL.md
```

The file is a product-neutral instruction artifact that defines:

- When Agentic Blender should be used.
- The required open-first behavior.
- Planning and acceptance-criteria format.
- Plan-review behavior and attempt limit.
- Tool usage rules.
- Programmatic verification.
- Screenshot and visual review.
- Fix-loop behavior and attempt limit.
- Export behavior.
- Final reporting requirements.
- Safety constraints.

The skill must not assume one specific agent vendor, model, sub-agent API, filesystem location, or configuration schema.

The Python package will bundle the canonical file under a resource path such as:

```text
src/agentic_blender/resources/agent/SKILL.md
```

The CLI must provide a generic way to print or copy the file, for example:

```powershell
agentic-blender help skill --print
agentic-blender help skill --output .\SKILL.md
```

The project must not include product-specific agent metadata in v0.1.0, including `agents/openai.yaml` or equivalent vendor descriptors.

The help output may explain that each agent product has its own method for registering MCP servers and installing instruction files, but it must present one canonical MCP descriptor and avoid maintaining per-product integration code.

## Alternatives Considered

### OpenAI-Specific Skill Metadata

Rejected because the project is not an OpenAI-only integration and the metadata would imply a support commitment to one product-specific packaging model.

### Separate Skill Packages for Every Agent Product

Rejected because they would duplicate the workflow, drift over time, and require continuous compatibility maintenance.

### No Skill File

Rejected because the MCP tool schemas alone do not express the required multi-step planning, review, verification, retry, export, and reporting workflow.

### Embed All Instructions Only in MCP Tool Descriptions

Rejected because tool descriptions should remain focused on individual operations and are not an appropriate replacement for an end-to-end orchestration policy.

### Automatically Modify Every Agent's Configuration

Rejected because configuration locations and schemas vary, may contain sensitive user settings, and would require vendor-specific implementation and testing.

## Consequences

### Positive

- One canonical workflow is maintained.
- The project remains agent-agnostic.
- Users can adapt the file to the conventions of their chosen agent.
- The CLI can expose the skill without knowing the agent product.
- Workflow updates do not need to be duplicated across integrations.

### Negative

- Users may need to manually place or adapt the file for their agent.
- Not every agent product uses the name `SKILL.md` or supports instruction files identically.
- Generic instructions cannot rely on one vendor's exact sub-agent invocation syntax.

## Implementation Requirements

- Bundle exactly one canonical generic `SKILL.md` in v0.1.0.
- Do not add `agents/openai.yaml` or other vendor-specific metadata.
- `agentic-blender help` must explain the generic installation concept.
- The CLI must support printing and copying the canonical file.
- Copy operations must reject accidental overwrite by default.
- The skill must match the final MCP tool names and schemas.
- The skill must describe reviewer roles conceptually and leave product-specific delegation syntax to the user's agent.
