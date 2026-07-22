# Decision 0011: Use a Bounded Plan, Review, Implement, Verify, Export Workflow

## Status

Accepted

## Date

2026-07-22

## Context

A successful Blender command does not prove that the requested visual result is correct. Agentic Blender also needs to avoid unstructured trial-and-error behavior, unsafe destructive actions, and infinite retry loops.

The product itself exposes tools, but the external agent is responsible for planning, delegating reviews, deciding which tools to call, interpreting verification results, and reporting completion.

The workflow instructions must remain usable across different MCP-capable agent products.

## Decision

The generic Agentic Blender skill must define this workflow:

```text
Open
→ Plan
→ Review the plan
→ Implement
→ Verify programmatically
→ Capture screenshot
→ Review visually
→ Fix when required
→ Export
→ Report
```

### Open

The agent must call `open_blender` before planning scene operations so the plan can account for actual Blender readiness and safety conditions.

### Plan

The plan must contain:

- The requested goal.
- Ordered implementation steps.
- Programmatic acceptance criteria.
- Visual acceptance criteria.
- Expected artifacts.
- Relevant safety constraints.

### Plan Review

A reviewer sub-agent evaluates the user request, plan, available tools, acceptance criteria, and safety constraints.

The reviewer returns either:

```text
PASS
```

or:

```text
FAIL
Reason: ...
Required changes: ...
```

The workflow allows a maximum of three total plan attempts, including the initial plan. After the third failure, the workflow stops and reports failure.

### Implementation

Only an approved plan may proceed to scene-editing operations.

### Programmatic Verification

The implementing agent must call `inspect_scene` and compare its structured result with the plan's programmatic acceptance criteria.

A known programmatic mismatch must be fixed before visual approval or explicitly reported as a failure.

### Visual Verification

After programmatic inspection, the agent captures a full Blender-window screenshot and asks a reviewer sub-agent to compare:

- The original user request.
- The approved plan.
- The screenshot.
- The scene summary.
- The visual acceptance criteria.

The reviewer returns `PASS` or `FAIL` with concrete required fixes.

The workflow allows a maximum of three total visual-review attempts, including the first screenshot review.

### Fix Loop

After a visual-review failure, the agent must apply the requested fix, rerun relevant programmatic inspection, capture a new screenshot, and request another review.

After the third visual failure, the agent stops retrying. It may preserve the Blender project as an explicitly unverified artifact when safe, but it must not report the task as successful.

### Export

A successful workflow exports only after programmatic and visual verification pass.

### Report

The final report includes:

- Overall status.
- Actions performed.
- Programmatic verification result.
- Visual verification result.
- Plan-attempt count.
- Visual-review-attempt count.
- Screenshot path.
- Blender project path.
- Final scene summary.
- Warnings and unresolved failures.

## Alternatives Considered

### Implement Immediately Without Planning

Rejected because it increases incorrect tool use, makes safety constraints easier to miss, and provides no explicit acceptance criteria.

### Self-Review Only

Rejected as the required workflow because an independent reviewer context is more likely to identify omissions and visual mismatches. The hosting agent product is responsible for providing sub-agent delegation.

### Visual Verification Only

Rejected because screenshots cannot reliably establish exact object names, types, transforms, project paths, or unsaved state.

### Programmatic Verification Only

Rejected because a structurally valid scene may still be framed poorly, visually obscured, or inconsistent with the user's visible intent.

### Unlimited Retries

Rejected because they can consume unbounded time and resources and conceal persistent tool or specification failures.

### Export Before Verification

Rejected for successful workflows because it creates final artifacts before quality gates pass. Failed work may be preserved only when explicitly marked unverified.

## Consequences

### Positive

- Tasks have explicit, testable acceptance criteria.
- Programmatic and visual evidence complement each other.
- Retry limits prevent infinite loops.
- The final report exposes verification quality and artifact locations.
- The workflow remains independent of a particular agent vendor.

### Negative

- Sub-agent reviews add latency and token cost.
- Not every MCP client provides identical sub-agent capabilities.
- The Blender extension needs a generic mechanism for receiving workflow status updates from the external agent.
- Small tasks require more process than direct tool calls.

## Implementation Requirements

- The bundled `SKILL.md` must encode this workflow.
- Plan and visual-review limits must both be three total attempts.
- Reviewer prompts must require strict PASS/FAIL outcomes and actionable failure details.
- Workflow status must be publishable to the Blender extension without product-specific metadata.
- The extension UI must show the current phase and attempt count.
- Successful completion requires both programmatic and visual verification.
- Final reporting must distinguish successful, failed, and preserved-but-unverified outcomes.
