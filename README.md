# COMP3161 VLE API

Introduction to Database Management Systems final project for a simple Virtual Learning Environment.

The project uses Flask, MySQL, deterministic seed data, Basic Auth for protected routes, and a Postman collection for a full demo workflow.

## Quick Setup

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Create `backend/.env` from `backend/.env.example` and set your local MySQL credentials.

Regenerate seed data when needed:

```powershell
.\.venv\Scripts\python.exe database\generate_seed_data.py
```

Rebuild the database:

```powershell
mysql -u root -p < database\schema.sql
mysql -u root -p Vle < database\generated_seed.sql
mysql -u root -p Vle < database\report_views.sql
```

Run the API:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1
```

Run the React frontend in a second terminal:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```

Or run the frontend manually:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

If dependencies are already installed, only run:

```powershell
cd frontend
npm.cmd run dev
```

The frontend reads its API base URL from `VITE_API_BASE_URL`. Copy `frontend/.env.example` to `frontend/.env` if you need to change the default local API URL.

## Current Project Shape

This repo is a Flask + MySQL coursework API for a simple Virtual Learning Environment.

- `backend/app.py` contains the API routes and shared helpers.
- `backend/` contains the Flask API, backend dependencies, and backend tests.
- `frontend/` contains the bonus React + Vite web application.
- `database/schema.sql` defines the main schema.
- `database/report_views.sql` defines the report views.
- `database/generate_seed_data.py` regenerates deterministic seed data into `database/generated_seed.sql`.
- `database/generated_seed.sql` is committed for easy local demo rebuilds even though it is generated.
- `scripts/` contains setup and start helpers.
- `postman/` contains the full local workflow collection and environment.

## Key Design Choices

- `CourseMember` is a read-only view derived from `Enrol` and `Teaches`.
- Basic Auth is the current temporary auth approach for protected routes.
- Each course has exactly one lecturer.
- `Enrol.grade` is derived from assignment grades.
- Course content and submission content are metadata/text, not real uploaded files.
- Seed data is deterministic so the team can rebuild the same demo state reliably.

## Documentation

- `docs/API_GUIDE.md` explains how to run, authenticate, test, and demo the system.
- `docs/DECISIONS.md` explains the important design choices, rationale, and current trade-offs.

## Postman

Import these files into Postman:

- `postman/VLE API Full Workflow.postman_collection.json`
- `postman/VLE Local.postman_environment.json`

Use `docs/demo_credentials.txt` for the seed student, lecturer, and admin credentials.
