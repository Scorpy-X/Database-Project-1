$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $RepoRoot "backend"
$VenvPath = Join-Path $RepoRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$EnvPath = Join-Path $BackendPath ".env"

Set-Location $RepoRoot

if (-not (Test-Path $PythonExe)) {
    throw "Python virtual environment not found. Run .\setup.bat or scripts\setup.ps1 first."
}

if (-not (Test-Path $EnvPath)) {
    throw "backend\.env not found. Run .\setup.bat, then update backend\.env with your MySQL credentials."
}

Write-Host "Starting Flask backend at http://127.0.0.1:5000 ..."
& $PythonExe -m flask --app backend.app run --host 127.0.0.1 --port 5000 --no-reload

if ($LASTEXITCODE -ne 0) {
    throw "Backend exited with code $LASTEXITCODE."
}
