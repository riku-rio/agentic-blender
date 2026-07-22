# Contributing to Agentic Blender

## Supported Contributor Environment

- **Operating system:** Windows 10/11 x64.
- **Python:** 3.11 for development.
- **Blender:** 5.2.0 LTS for Blender-dependent work.
- **Package manager:** `uv` installed and available in PowerShell.

## Repository Setup

1. Clone the repository.
2. Run `uv sync` to install dependencies.
3. Run `uv run pre-commit install` to configure pre-commit hooks.

## Running Quality Checks

Run all formatting, linting, type-checking, tests, and pre-commit hooks:

    .\scripts\quality.ps1

Run an individual check when needed:

    uv run ruff format --check .
    uv run ruff check .
    uv run mypy src/agentic_blender/
    uv run pytest tests/ -m "unit or integration"
    uv run pre-commit run --all-files

## Tests

- **Unit and integration tests:** Run with `uv run pytest tests/ -m "unit or integration"`.
- **Blender tests:** Require a self-hosted Windows x64 runner with Blender 5.2.0 LTS installed.

### Blender Smoke Tests

Blender smoke tests require a self-hosted Windows x64 runner with Blender 5.2.0 LTS.

The workflow is manual:

    Actions → Blender Smoke Tests → Run workflow

Run locally with:

    $env:AGENTIC_BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    uv run pytest tests/blender -m blender -v

## Commit Conventions

Use clear Conventional Commit-style prefixes such as:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `test:` — tests
- `chore:` — maintenance, tooling, dependencies

## Branch Conventions

Use descriptive branches:

- `feat/...` — new features
- `fix/...` — bug fixes
- `docs/...` — documentation changes
- `chore/...` — maintenance and tooling

## Pull Request Process

- Explain the scope of the change.
- Link related tasks or decisions.
- Include verification results.
- Keep unrelated changes out of the PR.

## License Acknowledgement

By contributing, you agree that your contributions are submitted under the GPL-3.0-or-later license.
