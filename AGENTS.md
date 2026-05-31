# Repository Working Instructions

This repo is a Flask + MySQL + React Virtual Learning Environment coursework/demo project.

## Project Rules

- Treat the root `.bat` files as the primary Windows demo interface.
- Use `npm.cmd` in Windows scripts to avoid PowerShell execution-policy friction.
- Do not call this project FastAPI; the backend is Flask.
- Keep public claims honest: this is a coursework/demo VLE, not a production LMS.
- Preserve user changes. Do not revert unrelated files.
- Keep screenshots deferred until they are manually captured and reviewed.
- Keep `scripts/` as optional PowerShell/manual tooling, not the main user path.

## Useful Commands

```powershell
cmd /c "set VLE_NO_PAUSE=1&& call test.bat"
.\.venv\Scripts\python.exe -m flask --app backend.app run --host 127.0.0.1 --port 5000 --no-reload
cd frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## Documentation Expectations

- README should be employer-facing and demo-first.
- Detailed API workflow belongs in `docs/API_GUIDE.md`.
- Design rationale belongs in `docs/DECISIONS.md`.
- Index evidence belongs in `docs/INDEX_EVIDENCE.md`.
- Continuation notes belong in `docs/ai/`.
