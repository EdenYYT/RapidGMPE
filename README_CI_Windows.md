# Plan A: Build Windows .exe from macOS using GitHub Actions

## Steps
1. Copy these files into your repo (same layout):
   - `.github/workflows/build-windows.yml`
   - `build_win.spec`
2. Commit & push to GitHub (`main` branch).
3. Open **Actions** → **Build Windows EXE** → **Run workflow** (or push again).
4. Download artifact **RapidGM-win** → inside `RapidGM` folder you'll find `RapidGM.exe`.

Notes:
- The spec collects PROJ/GDAL data for `pyproj`/`rasterio` to avoid missing-data errors.
- One-folder build is more reliable for these native libs.
- Change app name by editing `name='RapidGM'` in the spec.
- If your entry file is not `main_gui.py`, change it in `build_win.spec`.