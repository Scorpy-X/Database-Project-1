$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$FrontendPath = Join-Path $RepoRoot "frontend"
$EnvPath = Join-Path $FrontendPath ".env"
$EnvExamplePath = Join-Path $FrontendPath ".env.example"
$NodeModulesPath = Join-Path $FrontendPath "node_modules"
$PackageLockPath = Join-Path $FrontendPath "package-lock.json"
$LocalNpmCache = Join-Path $FrontendPath ".npm-cache"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FilePath,

        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

if (-not (Test-Path $FrontendPath)) {
    throw "Frontend folder not found at $FrontendPath"
}

Set-Location $FrontendPath

if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    throw "Node.js is not installed or is not available on PATH."
}

if (-not (Get-Command "npm.cmd" -ErrorAction SilentlyContinue)) {
    throw "npm.cmd is not installed or is not available on PATH."
}

if ((-not (Test-Path $EnvPath)) -and (Test-Path $EnvExamplePath)) {
    Copy-Item -Path $EnvExamplePath -Destination $EnvPath
    Write-Host "Created frontend/.env from frontend/.env.example."
}

$env:npm_config_cache = $LocalNpmCache

if (-not (Test-Path $NodeModulesPath)) {
    if (Test-Path $PackageLockPath) {
        Write-Host "Installing frontend dependencies with npm ci..."
        Invoke-Native "npm.cmd" @("ci")
    }
    else {
        Write-Host "Installing frontend dependencies with npm install..."
        Invoke-Native "npm.cmd" @("install")
    }
}
else {
    Write-Host "Using existing frontend node_modules."
}

Write-Host ""
Write-Host "Starting Vite frontend at http://127.0.0.1:5173 ..."
Invoke-Native "npm.cmd" @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173")
