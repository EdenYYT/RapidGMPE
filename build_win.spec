# build_win.spec — PyInstaller spec for Windows one-folder build
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('rasterio') + collect_submodules('pyproj')
datas = collect_data_files('pyproj') + collect_data_files('rasterio')

block_cipher = None

a = Analysis(
    ['main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='RapidGM', console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='RapidGM')