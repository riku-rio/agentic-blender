# Decision 0009: Capture the Full Blender Window on Windows

## Status

Accepted

## Date

2026-07-22

## Context

The v0.1.0 workflow requires visual verification after programmatic scene inspection. The reviewer must see the state of the visible Blender application, not only a render or viewport-only image generated inside Blender.

The screenshot implementation must identify the Blender window associated with the active session, handle Windows display scaling and multi-monitor coordinates, save a normal PNG artifact, and return image content usable by an MCP client.

No single selected library covers window identity, capture, and PNG validation equally well.

## Decision

Capture the full top-level Blender application window associated with the active session.

Use the libraries with these responsibilities:

- **`pywin32`**
  - Enumerate top-level Windows desktop windows.
  - Associate windows with the Blender process ID.
  - Read and restore window state.
  - Read window bounds.
  - Focus or bring the window forward where Windows permits.
  - Support DPI-awareness setup and Windows-specific metadata.

- **`mss`**
  - Capture the rectangular screen region occupied by the selected Blender window.
  - Handle monitor coordinate spaces, including negative coordinates where supported.

- **Pillow**
  - Open and validate the generated PNG.
  - Inspect dimensions and image format.
  - Perform minimal conversion or cropping only when required by the defined capture flow.

The required public screenshot mode in v0.1.0 is:

```text
full_blender_window
```

The output must include Blender's application chrome and visible UI so the reviewer can assess both scene state and relevant Agentic Blender status indicators.

### DPI and Multi-Monitor Policy

- The external process must opt into an appropriate Windows DPI-awareness mode before interpreting window coordinates.
- Capture coordinates must be expressed in the same physical-pixel coordinate space used by the capture backend.
- Negative X or Y coordinates must be supported for monitors positioned left of or above the primary monitor.
- Window bounds must be validated before capture.
- The saved PNG dimensions must match the validated capture rectangle, subject to documented Windows border behavior.

### Window State Policy

- If the bound Blender window is minimized, Agentic Blender may restore it before capture.
- The product should bring the window forward when practical but must not claim that Windows always permits forced focus.
- If no unambiguous window belongs to the bound Blender process, return `SCREENSHOT_FAILED` rather than capturing an arbitrary window.

## Alternatives Considered

### Blender Viewport Screenshot Only

Rejected because it omits application chrome, extension status UI, dialogs, and other context needed to verify the visible workflow.

### Blender Render Output

Rejected because v0.1.0 does not configure a production camera, lighting, or render pipeline, and a render would not prove the application UI state.

### `pyautogui`

Rejected because it is broad desktop automation, adds unnecessary input-control capabilities, and does not provide the desired process-bound window selection model.

### `pywinauto`

Rejected because v0.1.0 does not require general UI automation. `pywin32` provides the narrower Windows APIs required for process/window association and state handling.

### Pillow `ImageGrab` as the Sole Backend

Rejected because process-bound window discovery, restoration, DPI behavior, and multi-monitor handling still require Windows-specific logic.

### Capture the Entire Desktop

Rejected because it can expose unrelated user content, makes visual review less precise, and does not guarantee that the target Blender window is readable.

## Consequences

### Positive

- Visual reviewers receive the same Blender application state the user sees.
- Window selection is tied to the active Blender process.
- Responsibilities are divided between focused libraries.
- The strategy supports scaled displays and multi-monitor layouts.

### Negative

- The implementation is Windows-specific.
- Obscured portions of the Blender window may appear obscured because the strategy captures the visible desktop region rather than an off-screen window surface.
- Windows focus restrictions can prevent guaranteed foreground activation.
- DPI and border calculations require careful tests across machine configurations.

## Implementation Requirements

- `screenshot` must require an output directory and accept an optional filename.
- Generated filenames must include a collision-resistant timestamp.
- Existing files must not be overwritten by default.
- The active Blender process ID must be resolved to one unambiguous top-level window.
- The process must configure DPI awareness before reading capture coordinates.
- Minimized-window restoration must use bounded waits.
- Capture must use the full validated Blender window rectangle.
- The PNG must be validated with Pillow and have non-zero dimensions.
- The tool must return the absolute path, dimensions, timestamp, capture mode, and MCP-usable image content.
- Tests must cover standard scaling, non-100% scaling, negative monitor coordinates, minimized windows, ambiguous windows, invalid bounds, and filename collisions where practical.
