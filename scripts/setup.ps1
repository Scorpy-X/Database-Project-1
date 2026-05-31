$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $RepoRoot "backend"
$RequirementsPath = Join-Path $BackendPath "requirements.txt"
$VenvPath = Join-Path $RepoRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$TempPath = Join-Path $VenvPath "setup_tmp"

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

    Write-Host ""
    Write-Host "Setup complete."
    Write-Host "Activate the environment with:"
    Write-Host ".\.venv\Scripts\Activate.ps1"
}
finally {
    $env:TEMP = $OriginalTemp
    $env:TMP = $OriginalTmp

    if (Test-Path $TempPath) {
        Remove-Item -Recurse -Force -Path $TempPath -ErrorAction SilentlyContinue
    }
}
