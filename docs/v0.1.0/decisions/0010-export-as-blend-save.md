# Decision 0010: Implement export as a Normal Blender Project Save

## Status

Accepted

## Date

2026-07-22

## Context

The v0.1.0 workflow must produce a reusable Blender project artifact after verification. The public agent-facing operation should describe the workflow intent—producing the requested final artifact—without exposing unnecessary Blender API naming.

Blender uses normal project-save operations to create `.blend` files. Other Blender export operations usually target interchange formats such as FBX, OBJ, glTF, or USD, which are outside the first release.

The operation must also prevent accidental overwrite and verify that the artifact was actually created.

## Decision

Expose one public MCP tool named:

```text
export
```

In v0.1.0, `export` means saving the current Blender project as a `.blend` file using Blender's normal project-saving behavior.

The tool accepts:

- Required output directory.
- Optional filename.
- Explicit overwrite policy.

Behavior:

- If no filename is provided, generate a timestamp-based filename.
- Ensure the final filename ends with `.blend`.
- Refuse to overwrite an existing file by default.
- Validate the output directory before dispatching the Blender command.
- Save from inside Blender on the main thread.
- Verify externally that the final file exists and has non-zero size.
- Return the absolute path, byte size, Blender version, scene summary, and verification status.
- The v0.1.0 release test must reopen the saved project in Blender 5.2.0 LTS.

The public name remains `export` so future releases may add explicitly selected artifact formats without renaming the high-level workflow operation. Any future format support must use typed format inputs and separate decision records.

## Alternatives Considered

### Name the Tool `save_blend`

Rejected because it describes the current implementation rather than the agent's higher-level artifact-producing intent and would be awkward if typed export formats are added later.

### Name the Tool `save_project`

Rejected because the product workflow and user request commonly refer to exporting the final artifact. The result schema and documentation will make the `.blend` behavior explicit.

### Use Blender Interchange Export in v0.1.0

Rejected because the acceptance scenario requires a reopenable Blender project, not a flattened or lossy interchange file.

### Overwrite Existing Files by Default

Rejected because automatic overwrite can destroy user artifacts and violates the safe-by-default policy.

### Trust Blender's Success Response Without Filesystem Verification

Rejected because command completion alone does not prove that the expected file exists at the requested location.

## Consequences

### Positive

- The agent receives one clear artifact-generation tool.
- The complete editable Blender project is preserved.
- Overwrite protection reduces data-loss risk.
- External verification catches path and save failures.

### Negative

- The name `export` may initially suggest interchange formats, so documentation and tool descriptions must state that v0.1.0 produces `.blend` only.
- Reopen validation is more expensive than checking file existence and is primarily a smoke/release test rather than a check on every call.

## Implementation Requirements

- Output paths and filenames must be normalized and validated.
- The default overwrite policy must be false.
- Timestamp filenames must avoid normal collisions.
- Blender saving must run on Blender's main thread.
- The tool must return `OUTPUT_ALREADY_EXISTS`, `INVALID_OUTPUT_PATH`, or `EXPORT_FAILED` as appropriate.
- Successful responses must include an absolute path and non-zero file size.
- Automated or scripted release validation must reopen the file in Blender 5.2.0 LTS and inspect the expected scene.
