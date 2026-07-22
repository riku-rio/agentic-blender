# Decision 0013: License Agentic Blender Under GPL-3.0-or-Later

## Status

Accepted

## Date

2026-07-22

## Context

Agentic Blender includes a Blender extension that imports and uses Blender's Python API through `bpy`. Blender is distributed under the GNU General Public License, and Blender's official licensing guidance states that scripts and add-ons using Blender's Python API must use a GPL-compatible license when distributed.

The external CLI and MCP server are technically separable from Blender, but they are developed and distributed as one project with the extension, shared product identity, bundled resources, and a single release workflow.

The project needs one clear repository-wide license that is compatible with Blender integration, permits modification and redistribution, and avoids uncertainty about whether separate directories have different terms.

## Decision

License the Agentic Blender repository and distributed project under:

```text
GNU General Public License v3.0 or later
SPDX-License-Identifier: GPL-3.0-or-later
```

A root `LICENSE` file must contain the GPL version 3 license text.

Source files may use this SPDX identifier where license headers are appropriate:

```text
SPDX-License-Identifier: GPL-3.0-or-later
```

The same license applies to:

- The external Python CLI.
- The MCP server.
- The Blender extension.
- Bundled workflow resources such as `SKILL.md`.
- Project-maintained scripts and examples, unless a file explicitly identifies compatible third-party terms.

Documentation is distributed as part of the GPL-licensed repository unless a later decision adopts a separate compatible documentation license.

Third-party dependencies remain under their own licenses. Their inclusion must be reviewed for GPL compatibility and distribution obligations before release.

## Blender Compatibility Considerations

- The extension imports `bpy` and is intended to execute as part of Blender's extension environment.
- Distributed extension code must remain under GPL-compatible terms.
- The project must not copy Blender source code or third-party code without preserving required notices and license terms.
- Package metadata, extension metadata, release archives, and source distributions must identify the project license consistently.
- A dependency being installable from PyPI does not by itself establish license compatibility; dependency licenses must be reviewed.
- This decision records the project's engineering and distribution policy and is not a substitute for legal advice.

## Alternatives Considered

### MIT License

Rejected as the repository-wide license because the Blender extension directly uses Blender's Python API and the project should adopt an unambiguously GPL-compatible distribution model.

### Apache License 2.0

Rejected as the sole repository-wide license because the project benefits from using the same strong copyleft family as Blender and avoiding ambiguity around the extension's combined distribution.

### Separate Licenses for the External Server and Extension

Rejected for v0.1.0 because it would complicate packaging, contributions, notices, and user understanding. The components are designed and released as one product.

### GPL-2.0-or-Later

Not selected because GPL-3.0-or-later provides a clear modern baseline for the new project while retaining compatibility through the “or later” option.

### Proprietary License

Rejected because it would conflict with the intended open-source collaboration model and create serious compatibility concerns for the distributed Blender extension.

## Consequences

### Positive

- The project uses an explicit GPL-compatible license for Blender integration.
- Users may study, modify, and redistribute the complete project under clear terms.
- One repository-wide license simplifies packaging and contribution policy.
- Improvements distributed as modified versions remain available under compatible terms.

### Negative

- Organizations that require permissive-only dependencies may be unable to incorporate the project into proprietary distributions.
- Dependency and bundled-code license review remains necessary.
- Contributors and distributors must comply with GPL source and notice obligations.
- Dual licensing would require a future decision and appropriate contributor rights.

## Implementation Requirements

- Add a root `LICENSE` file containing GPL version 3.
- Set package metadata to `GPL-3.0-or-later` using the appropriate license expression.
- Set Blender extension metadata to a GPL-compatible identifier supported by the manifest format.
- Add license information to release artifacts and documentation.
- Review runtime and development dependency licenses before v0.1.0 release.
- Preserve third-party notices when required.
- Do not claim that this project decision constitutes legal advice.

## References

- Blender License: https://www.blender.org/about/license/
- GNU GPL version 3: https://www.gnu.org/licenses/gpl-3.0.html
