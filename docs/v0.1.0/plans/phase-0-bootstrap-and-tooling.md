# Phase 0 Implementation Plan — Repository Bootstrap and Tooling

## Document Status

* **Tasks covered:** REP-001–REP-013, QLT-001–QLT-012
* **Phase:** 0.2 Repository Bootstrap · 0.3 Tooling and Quality
* **Date:** 2026-07-22
* **Source tasks:** [TASKS.md §0.2–0.3](../TASKS.md)
* **Target branch:** `feat/phase-0-foundation`
* **Official environment:** Windows 10/11 x64 · Blender 5.2.0 LTS · Python 3.10+

---

## 1. Overview

This plan translates the remaining Phase 0 tasks into concrete, ordered implementation steps.

All decisions that govern these tasks are already accepted in DEC-001–DEC-013. No blocking decision remains before implementation begins.

This plan covers repository bootstrap and development tooling only. It does not implement Blender discovery, IPC, the Blender extension, MCP tools, or product workflows from later phases.

### Exit Criteria

Phase 0 is complete when:

* [ ] The project installs from a clean clone with `uv sync --frozen`.
* [ ] The package builds successfully with `uv build`.
* [ ] `ruff format --check`, `ruff check`, `mypy`, and `pytest` pass.
* [ ] Pre-commit hooks pass locally.
* [ ] The unified PowerShell quality script passes.
* [ ] Standard CI runs and reports green.
* [ ] Blender GUI tests remain excluded from standard CI.
* [ ] A documented manual strategy exists for future Blender smoke tests.

---

## 2. Ordering and Dependencies

```text
REP-001  ← start here: initialize the packaged uv project
  ├─ REP-002  create the src/ package layout
  ├─ REP-003  pin the development Python version
  ├─ REP-004  set requires-python
  ├─ REP-005  configure uv_build
  ├─ REP-006  add runtime dependencies and update uv.lock
  ├─ REP-007  add development dependencies and update uv.lock
  ├─ REP-008  commit uv.lock and .python-version
  ├─ REP-009  add .gitignore
  ├─ REP-010  add LICENSE
  ├─ REP-011  add CHANGELOG.md
  ├─ REP-012  add CONTRIBUTING.md
  └─ REP-013  add SECURITY.md

REP-006 and REP-007 must finish before:
  ├─ QLT-001  configure Ruff formatting
  ├─ QLT-002  configure Ruff linting
  ├─ QLT-003  configure mypy
  ├─ QLT-004  exclude Blender-embedded modules from external mypy checks
  ├─ QLT-005  configure pytest
  ├─ QLT-006  configure pytest-asyncio
  ├─ QLT-007  configure pytest-cov
  ├─ QLT-008  configure pre-commit
  └─ QLT-009  add the unified local quality command

QLT-001 through QLT-009 must finish before:
  ├─ QLT-010  add standard GitHub Actions CI
  ├─ QLT-011  exclude Blender GUI tests from standard CI
  └─ QLT-012  document and add the manual Blender smoke-test workflow
```

---

## 3. Step-by-Step Implementation

### Step 1 — Project Initialization (REP-001–REP-005)

Run from the repository root:

```powershell
uv init --package --name agentic-blender --python 3.11
```

`--package` creates a packaged application using the `src/` layout and configures a build backend.

If `pyproject.toml` already exists when implementation begins, do not run `uv init` over it. Edit the existing file manually and create only the missing package files.

The command may generate:

* A placeholder `main()` function.
* A temporary `[project.scripts]` entry.
* A generated package module.

Remove the placeholder CLI implementation and generated script entry. The real CLI entry point will be implemented during the CLI phase.

Set or verify the following project metadata in `pyproject.toml`:

```toml
[project]
name = "agentic-blender"
version = "0.1.0"
description = "Agent-agnostic MCP server and Blender extension."
readme = "README.md"
requires-python = ">=3.10"
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
dependencies = []

[build-system]
requires = ["uv_build>=0.11.30,<0.12"]
build-backend = "uv_build"
```

If the installed version of `uv init` generates a newer compatible `uv_build` lower bound, retain the generated lower bound and preserve the next-minor upper bound. Do not remove the upper bound.

Create or replace `src/agentic_blender/__init__.py` with:

```python
"""Agentic Blender package."""

__version__ = "0.1.0"
```

The initial package layout must be:

```text
src/
└── agentic_blender/
    └── __init__.py
```

Pin the development Python version:

```powershell
uv python pin 3.11
```

This creates `.python-version` containing:

```text
3.11
```

Verify the bootstrap:

```powershell
uv sync
uv run python --version
uv run python -c "import agentic_blender; print(agentic_blender.__version__)"
```

Expected results:

* `uv sync` succeeds.
* Python reports `3.11.x`.
* The package imports successfully.
* The printed package version is `0.1.0`.

---

### Step 2 — Runtime Dependencies (REP-006)

Add the following runtime dependencies:

| Package             | Constraint                       | Reason                                                                |
| ------------------- | -------------------------------- | --------------------------------------------------------------------- |
| `mcp[cli]`          | `>=1.28.1,<2`                    | Stable MCP SDK v1 line; v2 requires a separate compatibility decision |
| `pydantic`          | `>=2,<3`                         | Shared models and validation                                          |
| `pydantic-settings` | `>=2,<3`                         | Application configuration and environment settings                    |
| `typer`             | `>=0.12,<1`                      | CLI application                                                       |
| `rich`              | `>=13,<15`                       | Structured CLI output                                                 |
| `platformdirs`      | `>=4,<5`                         | Windows application path management                                   |
| `psutil`            | `>=6,<8`                         | Blender process discovery                                             |
| `pywin32`           | `>=306; sys_platform == 'win32'` | Windows process and window APIs                                       |
| `mss`               | `>=9,<11`                        | Screen capture                                                        |
| `Pillow`            | `>=10.3,<13`                     | PNG validation and image handling                                     |
| `filelock`          | `>=3.13,<4`                      | Launch, session, and installation locks                               |

Run:

```powershell
uv add `
  "mcp[cli]>=1.28.1,<2" `
  "pydantic>=2,<3" `
  "pydantic-settings>=2,<3" `
  "typer>=0.12,<1" `
  "rich>=13,<15" `
  "platformdirs>=4,<5" `
  "psutil>=6,<8" `
  "pywin32>=306; sys_platform == 'win32'" `
  "mss>=9,<11" `
  "Pillow>=10.3,<13" `
  "filelock>=3.13,<4"
```

Verify that `pywin32` is stored with its Windows environment marker. Do not make it an unconditional dependency and do not introduce a Windows optional extra in v0.1.0.

The committed `uv.lock` provides exact reproducible versions. The constraints in `pyproject.toml` define the supported dependency ranges.

> **MCP version checkpoint:** If implementation begins on or after 2026-07-27, re-check the official MCP Python SDK status before running this step. Keep the `<2` upper bound unless MCP v2 adoption is approved through a separate compatibility review and decision record.

---

### Step 3 — Development Dependencies (REP-007)

Add the development toolchain:

```powershell
uv add --dev `
  "ruff>=0.15,<0.16" `
  "mypy>=2.3,<3" `
  "pytest>=9.1,<10" `
  "pytest-asyncio>=1.4,<2" `
  "pytest-cov>=7.1,<8" `
  "pre-commit>=4.6,<5" `
  "types-psutil"
```

Do not add `types-Pillow`. Pillow versions in the selected runtime range already provide typing information.

After dependency resolution, record the installed versions:

```powershell
uv run ruff --version
uv run mypy --version
uv run pytest --version
uv run pre-commit --version
```

These versions must remain consistent with the pinned pre-commit hook revisions used in Step 14.

---

### Step 4 — Commit the Bootstrap and Lock Files (REP-008)

Review the generated files:

```powershell
git status --short
```

Commit the initial package bootstrap:

```powershell
git add pyproject.toml uv.lock .python-version src/
git commit -m "chore: initialize packaged project with uv"
```

Both `uv.lock` and `.python-version` must be committed.

Neither file may be added to `.gitignore`.

---

### Step 5 — `.gitignore` (REP-009)

Create `.gitignore` at the repository root.

It must cover:

* Python environments and bytecode:

  * `.venv/`
  * `__pycache__/`
  * `*.py[cod]`
  * `*$py.class`
* Distribution and package outputs:

  * `build/`
  * `dist/`
  * `*.egg-info/`
  * `.eggs/`
* Test and coverage output:

  * `.pytest_cache/`
  * `.coverage`
  * `.coverage.*`
  * `coverage.xml`
  * `htmlcov/`
* Tool caches:

  * `.mypy_cache/`
  * `.ruff_cache/`
  * `.hypothesis/`
  * `.tox/`
  * `.nox/`
* Editors:

  * `.vscode/`
  * `.idea/`
  * `*.suo`
  * `*.user`
* Windows artifacts:

  * `Thumbs.db`
  * `Desktop.ini`
  * `*.lnk`
* Local project overrides:

  * `*.local.toml`
  * `.env`
  * `.env.*`
  * `!.env.example`
* Generated Agentic Blender artifacts:

  * `artifacts/`
  * `screenshots/`
  * `exports/`

Do not ignore all ZIP files globally. Future Blender extension ZIP packages or test fixtures may be intentionally committed.

Do not ignore:

* `uv.lock`
* `.python-version`
* `LICENSE`
* Project documentation
* Workflow files
* Packaged resources

Use the GitHub Python `.gitignore` template as a starting point, then add the Windows-specific and Agentic Blender-specific entries above.

---

### Step 6 — LICENSE (REP-010)

Create `LICENSE` at the repository root containing the complete GNU General Public License Version 3 text.

Requirements:

1. Use the official GPL v3 license text.
2. Name the file exactly `LICENSE`.
3. Verify that it starts with:

   * `GNU GENERAL PUBLIC LICENSE`
   * `Version 3`
4. Keep the following project metadata in `pyproject.toml`:

```toml
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
```

This task records the project license selected by DEC-013. It does not replace legal review when distribution requirements change.

---

### Step 7 — CHANGELOG.md (REP-011)

Create `CHANGELOG.md` using Keep a Changelog structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- Initial project structure, package layout, and development tooling.
- Decision records for the foundational v0.1.0 choices.

[Unreleased]: https://github.com/riku-rio/agentic-blender/commits/main
```

Before the first release tag exists, the Unreleased link points to the `main` branch commit history.

After publishing `v0.1.0`, update the link references to:

```markdown
[Unreleased]: https://github.com/riku-rio/agentic-blender/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/riku-rio/agentic-blender/releases/tag/v0.1.0
```

Do not leave `<org>` or another repository-owner placeholder in the committed file.

---

### Step 8 — CONTRIBUTING.md (REP-012)

Create `CONTRIBUTING.md` at the repository root.

It must cover:

1. **Supported contributor environment**

   * Windows 10/11 x64.
   * Python 3.11 for development.
   * Blender 5.2.0 LTS for Blender-dependent work.
   * `uv` installed and available in PowerShell.
2. **Repository setup**

   * Clone the repository.
   * Run `uv sync`.
   * Run `uv run pre-commit install`.
3. **Local quality checks**

   * Run `.\scripts\quality.ps1`.
   * List the individual underlying commands.
4. **Tests**

   * Unit and integration tests.
   * Blender tests and their separate requirements.
5. **Commit conventions**

   * Use clear Conventional Commit-style prefixes such as `feat:`, `fix:`, `docs:`, `test:`, and `chore:`.
6. **Branch conventions**

   * Use descriptive branches such as `feat/...`, `fix/...`, `docs/...`, or `chore/...`.
7. **Pull request process**

   * Explain scope.
   * Link related tasks or decisions.
   * Include verification results.
   * Keep unrelated changes out of the PR.
8. **License acknowledgement**

   * Contributions are submitted under GPL-3.0-or-later.

A project-specific `CODE_OF_CONDUCT.md` is not required during Phase 0. Do not link to a nonexistent Code of Conduct file.

---

### Step 9 — SECURITY.md (REP-013)

Create `SECURITY.md` at the repository root.

It must contain:

1. **Supported versions**

   * Before `v0.1.0`, security fixes are applied to the active development branch.
   * After `v0.1.0`, the latest `v0.1.x` release receives security fixes unless a later policy supersedes it.
2. **Private reporting mechanism**

   * Use GitHub Private Vulnerability Reporting.
   * Do not request vulnerability reports through public issues.
3. **Response expectations**

   * Acknowledge a report within 5 business days.
   * Provide initial triage within 10 business days.
   * Provide a status update every 14 days while the investigation remains open.
4. **Responsible disclosure**

   * Ask reporters not to disclose the issue publicly before a fix or coordinated disclosure date.
5. **Scope**

   * Agentic Blender code and packaged resources are in scope.
   * Blender itself and vulnerabilities exclusively in third-party dependencies are outside the project's direct maintenance scope, though dependency reports may still be forwarded or mitigated.
6. **No guarantee of a fixed resolution date**

   * Resolution timing depends on severity, reproducibility, and upstream dependencies.

Enable GitHub Private Vulnerability Reporting in repository settings before relying on this policy publicly.

---

### Step 10 — Ruff Formatting (QLT-001)

Add to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

Verify:

```powershell
uv run ruff format --check .
```

---

### Step 11 — Ruff Lint Rules (QLT-002)

Add to `pyproject.toml`:

```toml
[tool.ruff.lint]
select = [
  "E",    # pycodestyle errors
  "W",    # pycodestyle warnings
  "F",    # Pyflakes
  "I",    # import sorting
  "N",    # naming
  "UP",   # Python upgrades
  "B",    # bugbear
  "C4",   # comprehensions
  "SIM",  # simplifications
  "TCH",  # type-checking imports
  "ANN",  # annotations
  "D",    # docstrings
]
ignore = [
  "D100", # public module docstring
  "D104", # public package docstring
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["agentic_blender"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["D"]
```

The `ANN101` and `ANN102` rules must not be listed; they are no longer active Ruff rules.

Verify:

```powershell
uv run ruff check .
```

---

### Step 12 — mypy Configuration (QLT-003 and QLT-004)

Add to `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true
disallow_any_generics = true
show_error_codes = true
pretty = true

# Blender extension modules run inside Blender's embedded Python environment.
# They are excluded from external-environment mypy checks.
exclude = [
  "^src/agentic_blender/resources/extension/",
]

[[tool.mypy.overrides]]
module = [
  "mss.*",
  "win32api",
  "win32con",
  "win32gui",
  "win32process",
  "pywintypes",
]
ignore_missing_imports = true
```

The exclusion path must match the planned extension location:

```text
src/agentic_blender/resources/extension/
```

Do not exclude all of `src/agentic_blender/resources/`; non-Blender Python resources may still require type checking later.

Verify:

```powershell
uv run mypy src/agentic_blender/
```

---

### Step 13 — pytest, pytest-asyncio, and Coverage (QLT-005–QLT-007)

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
  "--strict-markers",
  "--tb=short",
  "--cov=agentic_blender",
  "--cov-report=term-missing",
  "--cov-report=xml:coverage.xml",
  "--cov-fail-under=70",
]
markers = [
  "unit: fast isolated unit tests without Blender",
  "integration: tests using the filesystem or a fake IPC bridge",
  "blender: tests requiring a supported Blender installation",
]
```

Create the initial test structure:

```powershell
New-Item -ItemType Directory -Path tests -Force
New-Item -ItemType File -Path tests\__init__.py -Force
```

Create `tests/test_package.py`:

```python
"""Package bootstrap tests."""

import pytest

import agentic_blender


@pytest.mark.unit
def test_package_version() -> None:
    """Verify that the package exposes the expected initial version."""
    assert agentic_blender.__version__ == "0.1.0"
```

This test ensures that:

* pytest collects at least one test.
* The package is importable.
* Initial package metadata is covered.
* The configured coverage threshold can pass during Phase 0.

Verify:

```powershell
uv run pytest tests/ -m "unit or integration"
```

A run that collects zero tests is not acceptable.

---

### Step 14 — Pre-commit Hooks (QLT-008)

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.14
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: debug-statements

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        pass_filenames: false
        args: [src/agentic_blender/]
        types: [python]
```

The local mypy hook deliberately uses the project's `uv` environment. This prevents the pre-commit hook from maintaining a second, incomplete dependency environment.

Install and verify:

```powershell
uv run pre-commit install
uv run pre-commit run --all-files
```

Version policy:

* Ruff's pre-commit revision must match the selected Ruff tool line.
* Hook updates must be reviewed and committed intentionally.
* Do not use floating branches such as `main` for hook revisions.
* Run `uv run pre-commit autoupdate` only as an intentional dependency-maintenance change.

---

### Step 15 — Unified Local Quality Command (QLT-009)

Create the scripts directory:

```powershell
New-Item -ItemType Directory -Path scripts -Force
```

Create `scripts/quality.ps1`:

```powershell
$ErrorActionPreference = "Stop"

$commands = @(
    @("run", "ruff", "format", "--check", "."),
    @("run", "ruff", "check", "."),
    @("run", "mypy", "src/agentic_blender/"),
    @("run", "pytest", "tests/", "-m", "unit or integration"),
    @("run", "pre-commit", "run", "--all-files")
)

foreach ($command in $commands) {
    & uv @command
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        Write-Error "Command failed: uv $($command -join ' ')"
        exit $exitCode
    }
}

Write-Host "All quality checks passed."
```

The script must:

* Stop after the first failed native command.
* Return the failed command's non-zero exit code.
* Work in Windows PowerShell and PowerShell 7.
* Avoid relying only on `$ErrorActionPreference` for native process failures.

Document in `CONTRIBUTING.md`:

```markdown
## Running Quality Checks

Run all formatting, linting, type-checking, tests, and pre-commit hooks:

    .\scripts\quality.ps1

Run an individual check when needed:

    uv run ruff format --check .
    uv run ruff check .
    uv run mypy src/agentic_blender/
    uv run pytest tests/ -m "unit or integration"
    uv run pre-commit run --all-files
```

Verify:

```powershell
.\scripts\quality.ps1
```

---

### Step 16 — Standard GitHub Actions CI (QLT-010 and QLT-011)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  quality:
    name: Python ${{ matrix.python-version }}
    runs-on: windows-latest
    timeout-minutes: 20

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true

      - name: Install Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install locked dependencies
        run: uv sync --frozen --python ${{ matrix.python-version }}

      - name: Check formatting
        run: uv run --frozen ruff format --check .

      - name: Lint
        run: uv run --frozen ruff check .

      - name: Type-check
        run: uv run --frozen mypy src/agentic_blender/

      - name: Test unit and integration suites
        run: uv run --frozen pytest tests/ -m "unit or integration"

      - name: Run pre-commit hooks
        if: matrix.python-version == '3.11'
        run: uv run --frozen pre-commit run --all-files

      - name: Build distributions
        if: matrix.python-version == '3.11'
        run: uv build
```

Standard CI must not:

* Install Blender.
* Launch Blender.
* Execute tests marked `blender`.
* Depend on a graphical desktop session.
* Pretend that Blender GUI coverage is provided by `windows-latest`.

The Python matrix covers every Python version currently declared by the stable MCP v1 package and the project's `requires-python = ">=3.10"` policy.

---

### Step 17 — Blender Smoke-Test Strategy (QLT-012)

Create `.github/workflows/blender-smoke.yml`:

```yaml
name: Blender Smoke Tests

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  smoke:
    name: Blender 5.2.0 LTS
    runs-on: [self-hosted, windows, x64, blender]
    timeout-minutes: 30

    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true

      - name: Install Python 3.11
        run: uv python install 3.11

      - name: Install locked dependencies
        run: uv sync --frozen --python 3.11

      - name: Validate Blender executable
        shell: powershell
        run: |
          if (-not $env:AGENTIC_BLENDER_EXE) {
              throw "AGENTIC_BLENDER_EXE is not configured."
          }

          if (-not (Test-Path $env:AGENTIC_BLENDER_EXE)) {
              throw "Configured Blender executable does not exist: $env:AGENTIC_BLENDER_EXE"
          }
        env:
          AGENTIC_BLENDER_EXE: ${{ vars.BLENDER_EXE_PATH }}

      - name: Run Blender smoke tests when implemented
        shell: powershell
        run: |
          if (-not (Test-Path "tests\blender")) {
              Write-Warning "No Blender smoke-test directory exists yet; strategy validation only."
              exit 0
          }

          uv run --frozen pytest tests/blender -m blender -v

          if ($LASTEXITCODE -ne 0) {
              exit $LASTEXITCODE
          }
        env:
          AGENTIC_BLENDER_EXE: ${{ vars.BLENDER_EXE_PATH }}
```

Runner requirements:

* Self-hosted Windows x64 runner.
* Blender 5.2.0 LTS installed.
* Runner label `blender`.
* Repository variable `BLENDER_EXE_PATH` containing the full Blender executable path.
* An interactive desktop session available when future screenshot or visible-window tests require it.

Document in `CONTRIBUTING.md`:

```markdown
## Blender Smoke Tests

Blender smoke tests require a self-hosted Windows x64 runner with Blender 5.2.0 LTS.

The workflow is manual:

    Actions → Blender Smoke Tests → Run workflow

Run locally with:

    $env:AGENTIC_BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    uv run pytest tests/blender -m blender -v
```

The workflow may report a strategy-only success while `tests/blender/` does not yet exist. Once Blender tests are added, the workflow must execute them and propagate failures.

---

## 4. File Checklist

After completing all steps, the repository must contain:

| File or Directory                     | Task(s)                          | Purpose                                                  |
| ------------------------------------- | -------------------------------- | -------------------------------------------------------- |
| `pyproject.toml`                      | REP-001–REP-007, QLT-001–QLT-007 | Package metadata, dependencies, and tool configuration   |
| `uv.lock`                             | REP-006–REP-008                  | Reproducible dependency lock                             |
| `.python-version`                     | REP-003, REP-008                 | Development Python pin                                   |
| `src/agentic_blender/__init__.py`     | REP-002                          | Initial importable package and version metadata          |
| `.gitignore`                          | REP-009                          | Python, Windows, tool, and generated artifact exclusions |
| `LICENSE`                             | REP-010                          | Full GPL v3 license text                                 |
| `CHANGELOG.md`                        | REP-011                          | Keep a Changelog release history                         |
| `CONTRIBUTING.md`                     | REP-012, QLT-009, QLT-012        | Contributor setup and workflows                          |
| `SECURITY.md`                         | REP-013                          | Private disclosure and supported-version policy          |
| `.pre-commit-config.yaml`             | QLT-008                          | Ruff, mypy, and repository hygiene hooks                 |
| `tests/__init__.py`                   | QLT-005                          | Initial tests package                                    |
| `tests/test_package.py`               | QLT-005, QLT-007                 | Bootstrap package and coverage test                      |
| `scripts/quality.ps1`                 | QLT-009                          | Unified PowerShell quality command                       |
| `.github/workflows/ci.yml`            | QLT-010, QLT-011                 | Standard non-Blender CI                                  |
| `.github/workflows/blender-smoke.yml` | QLT-012                          | Manual self-hosted Blender test strategy                 |

---

## 5. Verification Sequence

Run the following on a clean clone after all Phase 0 files are committed:

```powershell
# 1. Install the exact locked environment.
uv sync --frozen

# 2. Build the source distribution and wheel.
uv build

# 3. Verify formatting.
uv run --frozen ruff format --check .

# 4. Verify lint rules.
uv run --frozen ruff check .

# 5. Verify static typing.
uv run --frozen mypy src/agentic_blender/

# 6. Run unit and integration tests with coverage.
uv run --frozen pytest tests/ -m "unit or integration"

# 7. Run all pre-commit hooks.
uv run --frozen pre-commit run --all-files

# 8. Verify the unified local wrapper.
.\scripts\quality.ps1
```

All eight commands must exit with code `0`.

After the branch is pushed:

1. Open or update the Phase 0 pull request.
2. Confirm that every standard CI matrix job passes.
3. Confirm that no standard CI job attempts to install or launch Blender.
4. Confirm that the manual Blender workflow is visible in GitHub Actions.
5. Do not mark QLT-012 as full Blender test coverage; it establishes the separate workflow strategy only.

---

## 6. Resolved Questions

| #  | Decision                                                                     | Required Implementation                                                                                |
| -- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Q1 | The repository is hosted under the personal GitHub account `riku-rio`.       | Use `riku-rio/agentic-blender` in changelog and repository references.                                 |
| Q2 | `pywin32` is a normal runtime dependency with `sys_platform == 'win32'`.     | Use an environment marker; do not make it unconditional or create an optional extra.                   |
| Q3 | The project remains on the stable MCP v1 line using `mcp[cli]>=1.28.1,<2`.   | Re-evaluate after 2026-07-27; MCP v2 adoption requires a separate decision.                            |
| Q4 | Vulnerabilities are reported through GitHub Private Vulnerability Reporting. | Enable the feature and document the 5-day acknowledgement, 10-day triage, and 14-day update targets.   |
| Q5 | A project-specific Code of Conduct is not required for Phase 0.              | Do not reference a nonexistent file; add one before actively soliciting broad community contributions. |

No open question blocks Phase 0 implementation.

---

## 7. Recommended Commit Boundaries

The implementation may use the following commit sequence:

```text
chore: initialize packaged project with uv
chore: add repository community and license files
chore: configure linting typing and tests
chore: add pre-commit and local quality script
ci: add standard and Blender smoke workflows
docs: mark Phase 0 bootstrap and tooling tasks complete
```

Each commit must be internally consistent and should pass the checks available at that point.

Do not mark REP or QLT tasks complete in `TASKS.md` until their implementation and verification are complete.

---

## 8. Final Definition of Done

Phase 0.2 and Phase 0.3 are complete when:

1. A clean clone installs with `uv sync --frozen`.
2. The package imports as `agentic_blender`.
3. `uv build` creates a source distribution and wheel.
4. The Python development version is pinned to 3.11.
5. The package declares support for Python 3.10 and newer.
6. Runtime and development dependencies are locked.
7. GPL-3.0-or-later licensing is present in metadata and `LICENSE`.
8. Contributor, changelog, and security documentation exist.
9. Ruff formatting and lint checks pass.
10. Strict mypy checks pass for the external package.
11. Blender extension sources are excluded from external mypy checks using the planned extension path.
12. Unit tests are collected and pass.
13. The initial coverage threshold passes.
14. Pre-commit hooks pass.
15. `scripts/quality.ps1` passes and propagates failures.
16. Standard Windows CI passes across Python 3.10–3.14.
17. Standard CI does not execute Blender tests.
18. The manual self-hosted Blender smoke-test strategy exists.
19. The Phase 0 task checklist is updated only after verification.
