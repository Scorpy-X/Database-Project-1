# Screenshot Capture Checklist

Screenshots are deferred until they can be manually reviewed. Do not commit low-value or partially loaded captures.

## Required Files

Save these images in this folder:

- `login.png`
- `student-dashboard.png`
- `course-detail.png`
- `lecturer-dashboard.png`
- `admin-reports.png`

## Capture Steps

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
6. Capture the five screenshots listed above.
7. Verify each screenshot has loaded data and no unrelated app/browser content.

## README Embed Pattern

After the screenshots are reviewed, replace the README placeholder section with image embeds such as:

```md
| Login | Student Dashboard |
| --- | --- |
| ![Login](docs/screenshots/login.png) | ![Student dashboard](docs/screenshots/student-dashboard.png) |
```
