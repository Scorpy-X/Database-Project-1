# Screenshot Maintenance

These screenshots are used by the project README. Keep only reviewed, cropped app screenshots in the README preview.

## Expected Files

The main screenshot set is:

- `login.png`
- `student-dashboard.png`
- `course-detail.png`
- `lecturer-dashboard.png`
- `admin-reports.png`
- `admin-users.png`

## Retake Steps

1. Run `setup.bat` if dependencies are not installed.
2. Rebuild the local database if you need a clean demo state:

```powershell
mysql -u root -p < database\schema.sql
mysql -u root -p Vle < database\generated_seed.sql
mysql -u root -p Vle < database\report_views.sql
```

3. Run `start_dev.bat`.
4. Open `http://127.0.0.1:5173`.
5. Use the accounts in `docs/demo_credentials.txt`.
6. Capture the screens listed above.
7. Crop out browser tabs, address bars, extension icons, and desktop chrome.
8. Verify each screenshot has loaded data and no broken text encoding before replacing the existing files.

Retake screenshots after major UI changes so the README continues to match the actual app.
