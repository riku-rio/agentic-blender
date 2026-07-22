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
