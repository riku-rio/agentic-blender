# Decision 0008: Expose One General add_primitive Tool

## Status

Accepted

## Date

2026-07-22

## Context

The first release needs a small set of mesh-creation capabilities, including the sphere used by the end-to-end acceptance scenario.

Blender exposes separate operators for different primitive types, and some operators use implementation-specific names such as UV Sphere. Mirroring every Blender operator as a separate MCP tool would create a large, inconsistent public API and make agents discover and reason about many nearly identical tools.

The public API should describe user intent rather than Blender operator naming details.

## Decision

Expose one typed MCP tool named:

```text
add_primitive
```

The tool accepts a required `primitive_type` plus shared transform and sizing inputs.

The supported v0.1.0 public primitive names are:

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

The extension maps public names to Blender implementation details.

Required convenience mappings include:

- `sphere` maps to Blender's UV Sphere operation.
- `square` maps to a plane primitive.
- `triangle` maps to a filled three-vertex mesh, implemented through the most stable Blender 5.2.0 LTS operation available.

The public API must use `sphere`, not `uv_sphere`, for the normal sphere case.

Shared inputs include:

- Optional object name.
- Location.
- Rotation.
- Scale.
- Size.

Primitive-specific optional inputs may be added where needed, but they must be typed and validated rather than passed as an unstructured options dictionary.

Lights, cameras, text, curves, materials, and advanced mesh operations are not primitives under this tool and require future dedicated tools.

## Alternatives Considered

### One MCP Tool Per Primitive

Examples would include `add_cube`, `add_uv_sphere`, `add_cylinder`, and `add_torus`.

Rejected because the tools would repeat the same transform, naming, validation, response, and error behavior while exposing Blender-specific implementation details.

### A Generic `add_shape` Tool

Rejected because “shape” is ambiguous across mesh primitives, curves, text, lights, cameras, and 2D concepts. `add_primitive` matches Blender terminology and clearly limits scope.

### A Generic Blender Operator Tool

Rejected because passing arbitrary operator names and arguments would effectively expose unbounded execution, weaken validation, and couple agents tightly to Blender internals.

### Only Add the Sphere in v0.1.0

Rejected because the general primitive dispatch architecture is foundational, and the additional basic primitives are low-risk once the typed mapping is implemented.

## Consequences

### Positive

- Agents discover one consistent creation tool.
- Shared transform and result behavior is implemented once.
- Public terminology is stable even if internal Blender operators change.
- New basic primitives can be added through a controlled enumeration.

### Negative

- The implementation must dispatch and validate primitive-specific options.
- A single tool schema may grow as more primitive options are supported.
- Some convenience names do not map one-to-one to Blender operator names.

## Implementation Requirements

- `primitive_type` must be a closed enumeration for v0.1.0.
- Unknown values must return `UNSUPPORTED_PRIMITIVE`.
- Every operation must return the requested primitive type, final object name, Blender object type, transform, and dimensions when available.
- Object creation must execute inside Blender on the main thread.
- Default values must be deterministic and documented.
- Tests must cover every public primitive, aliases, invalid primitive values, naming, and transforms.
