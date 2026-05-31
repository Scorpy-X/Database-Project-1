@echo off
setlocal
cd /d "%~dp0"

if not exist "frontend" (
  echo Frontend folder not found.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

if not exist "frontend\.env" (
  if exist "frontend\.env.example" (
    type "frontend\.env.example" > "frontend\.env"
    echo Created frontend\.env from frontend\.env.example.
  )
)

pushd frontend

if not exist "node_modules" (
  if exist "package-lock.json" (
    echo Installing frontend dependencies with npm ci...
    call npm.cmd ci
  ) else (
    echo Installing frontend dependencies with npm install...
    call npm.cmd install
  )
  if errorlevel 1 (
    popd
    echo Frontend dependency install failed.
    if not "%VLE_NO_PAUSE%"=="1" pause
    exit /b 1
  )
)

echo Starting Vite frontend at http://127.0.0.1:5173 ...
call npm.cmd run dev -- --host 127.0.0.1 --port 5173

popd
echo.
echo Frontend stopped.
if not "%VLE_NO_PAUSE%"=="1" pause
