@echo off
setlocal
cd /d "%~dp0"

echo === VLE local setup ===

if not exist "backend\.env" (
  if exist "backend\.env.example" (
    type "backend\.env.example" > "backend\.env"
    echo Created backend\.env from backend\.env.example.
    echo Edit backend\.env and set DB_PASSWORD before starting the backend.
  )
)

if not exist "frontend\.env" (
  if exist "frontend\.env.example" (
    type "frontend\.env.example" > "frontend\.env"
    echo Created frontend\.env from frontend\.env.example.
  )
)

if not exist ".venv" (
  echo Creating Python virtual environment at .venv...
  py -3.12 -m venv .venv 2>nul || py -3 -m venv .venv || python -m venv .venv
  if errorlevel 1 (
    echo Failed to create .venv. Install Python 3 and try again.
    pause
    exit /b 1
  )
) else (
  echo Using existing .venv.
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo Failed to activate .venv.
  pause
  exit /b 1
)

echo Installing backend requirements...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
python -m pip install -r "backend\requirements.txt"
if errorlevel 1 goto :fail

if not exist "frontend" (
  echo Frontend folder not found.
  pause
  exit /b 1
)

pushd frontend
if exist "package-lock.json" (
  echo Installing frontend dependencies with npm ci...
  call npm.cmd ci
) else (
  echo Installing frontend dependencies with npm install...
  call npm.cmd install
)
if errorlevel 1 (
  popd
  goto :fail
)
popd

echo.
echo Setup complete.
echo Next: update backend\.env if needed, then double-click start_dev.bat.
if not "%VLE_NO_PAUSE%"=="1" pause
exit /b 0

:fail
echo.
echo Setup failed. Check the error above.
if not "%VLE_NO_PAUSE%"=="1" pause
exit /b 1
