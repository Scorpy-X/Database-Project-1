# VLE Frontend

React + Vite frontend for the COMP3161 VLE project.

## Local Run

From the repository root, use the double-click batch file:

```powershell
start_frontend.bat
```

Or use the PowerShell helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```

Or run manually:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

The frontend reads the backend URL from `VITE_API_BASE_URL`. Copy `.env.example` to `.env` if the Flask API is not running at `http://127.0.0.1:5000`.
