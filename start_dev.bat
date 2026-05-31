@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo .venv not found. Run setup.bat first.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo frontend\node_modules not found. Run setup.bat first.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

start "VLE Backend" cmd /k ""%~dp0start_backend.bat""
start "VLE Frontend" cmd /k ""%~dp0start_frontend.bat""
timeout /t 3 >nul
start "" "http://127.0.0.1:5173"

echo Opened backend and frontend in separate terminal windows.
exit /b 0
