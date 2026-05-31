@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo .venv not found. Run setup.bat first.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

if not exist "backend\.env" (
  if exist "backend\.env.example" (
    type "backend\.env.example" > "backend\.env"
    echo Created backend\.env from backend\.env.example.
  )
  echo Update backend\.env with your MySQL credentials, then run this again.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
echo Starting Flask backend at http://127.0.0.1:5000 ...
python -m flask --app backend.app run --host 127.0.0.1 --port 5000 --no-reload

echo.
echo Backend stopped.
if not "%VLE_NO_PAUSE%"=="1" pause
