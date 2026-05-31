$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $RepoRoot "backend"
$FrontendPath = Join-Path $RepoRoot "frontend"
$RequirementsPath = Join-Path $BackendPath "requirements.txt"
$VenvPath = Join-Path $RepoRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$TempPath = Join-Path $VenvPath "setup_tmp"
$BackendEnvPath = Join-Path $BackendPath ".env"
$BackendEnvExamplePath = Join-Path $BackendPath ".env.example"
$FrontendEnvPath = Join-Path $FrontendPath ".env"
$FrontendEnvExamplePath = Join-Path $FrontendPath ".env.example"
$FrontendNodeModulesPath = Join-Path $FrontendPath "node_modules"
$FrontendPackageLockPath = Join-Path $FrontendPath "package-lock.json"

Set-Location $RepoRoot

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

function Invoke-NativeSuccess {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FilePath,

        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        & $FilePath @Arguments
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
}

function Test-PipAvailable {
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"

    try {
        & $PythonExe -m pip --version *> $null
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
}

$OriginalTemp = $env:TEMP
$OriginalTmp = $env:TMP

try {
    New-Item -ItemType Directory -Force -Path $TempPath | Out-Null
    $env:TEMP = $TempPath
    $env:TMP = $TempPath

    if (-not (Test-Path $PythonExe)) {
        Write-Host "Creating virtual environment at .venv..."
        Invoke-Native "py" @("-3", "-m", "venv", $VenvPath)
    }
    else {
        Write-Host "Virtual environment already exists at .venv."
    }

    if (-not (Test-PipAvailable)) {
        Write-Host "Bootstrapping pip..."
        if (-not (Invoke-NativeSuccess $PythonExe @("-m", "ensurepip", "--upgrade"))) {
            Write-Host "ensurepip failed; using system pip to seed the virtual environment..."
            Invoke-Native "py" @("-3", "-m", "pip", "--python", $VenvPath, "install", "--upgrade", "pip")
        }
    }

    Write-Host "Upgrading pip..."
    Invoke-Native $PythonExe @("-m", "pip", "install", "--upgrade", "pip")

    Write-Host "Installing backend requirements..."
    Invoke-Native $PythonExe @("-m", "pip", "install", "-r", $RequirementsPath)

    if ((-not (Test-Path $BackendEnvPath)) -and (Test-Path $BackendEnvExamplePath)) {
        Copy-Item -Path $BackendEnvExamplePath -Destination $BackendEnvPath
        Write-Host "Created backend/.env from backend/.env.example. Check DB_PASSWORD before starting the API."
    }

    if ((-not (Test-Path $FrontendEnvPath)) -and (Test-Path $FrontendEnvExamplePath)) {
        Copy-Item -Path $FrontendEnvExamplePath -Destination $FrontendEnvPath
        Write-Host "Created frontend/.env from frontend/.env.example."
    }

    if (-not (Test-Path $FrontendPath)) {
        throw "Frontend folder not found at $FrontendPath"
    }

    if (-not (Get-Command "npm.cmd" -ErrorAction SilentlyContinue)) {
        throw "npm.cmd is not installed or is not available on PATH."
    }

    Push-Location $FrontendPath
    try {
        if (-not (Test-Path $FrontendNodeModulesPath)) {
            if (Test-Path $FrontendPackageLockPath) {
                Write-Host "Installing frontend dependencies with npm ci..."
                Invoke-Native "npm.cmd" @("ci")
            }
            else {
                Write-Host "Installing frontend dependencies with npm install..."
                Invoke-Native "npm.cmd" @("install")
            }
        }
        else {
            Write-Host "Frontend node_modules already exists."
        }
    }
    finally {
        Pop-Location
    }

    Write-Host ""
    Write-Host "Setup complete."
    Write-Host "Start both apps with .\start_dev.bat, or start them separately with start_backend.bat and start_frontend.bat."
}
finally {
    $env:TEMP = $OriginalTemp
    $env:TMP = $OriginalTmp

    if (Test-Path $TempPath) {
        Remove-Item -Recurse -Force -Path $TempPath -ErrorAction SilentlyContinue
    }
}
