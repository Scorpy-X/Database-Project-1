@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Run setup.bat first.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

echo Running backend tests...
".venv\Scripts\python.exe" -m unittest discover -s backend\tests -v
if errorlevel 1 goto :fail

echo Running backend/database compile check...
".venv\Scripts\python.exe" -m compileall -q backend database
if errorlevel 1 goto :fail

if not exist "frontend\node_modules" (
  echo frontend\node_modules not found. Run setup.bat first.
  if not "%VLE_NO_PAUSE%"=="1" pause
  exit /b 1
)

pushd frontend
echo Running frontend build...
call npm.cmd run build
if errorlevel 1 (
  popd
  goto :fail
)

echo Running frontend lint...
call npm.cmd run lint
if errorlevel 1 (
  popd
  goto :fail
)

echo Running calendar color tests...
call node --test src\lib\calendarColors.test.mjs
if errorlevel 1 (
  popd
  goto :fail
)
popd

echo.
echo Test checks completed.
if not "%VLE_NO_PAUSE%"=="1" pause
exit /b 0

:fail
echo.
echo Test checks failed. Check the error above.
if not "%VLE_NO_PAUSE%"=="1" pause
exit /b 1
