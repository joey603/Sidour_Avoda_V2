# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Configuration pour inclure les DLLs Python
block_cipher = None

# Collecter les données nécessaires
datas = []
datas += collect_data_files('ttkbootstrap')
datas += collect_data_files('PIL')

# Ajouter le dossier assets
assets_path = 'assets'
if os.path.exists(assets_path):
    datas.append((assets_path, 'assets'))

# Configuration de l'exécutable
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'ttkbootstrap',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'sqlite3',
        'threading',
        'datetime',
        'random',
        'json',
        'csv',
        'urllib.request',
        'urllib.parse',
        'tempfile',
        'subprocess',
        'ctypes',
        'sys',
        'os',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Configuration pour inclure les DLLs Python
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = 'assets/app.ico' if os.path.exists('assets/app.ico') else ( 'assets/calender-2389150_960_720.png' if os.path.exists('assets/calender-2389150_960_720.png') else None )

# Configuration de l'exécutable (structure standard PyInstaller)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SidourAvoda',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Application GUI sans console
    disable_windowed_traceback=False,
    icon=icon_path,
)

# Regrouper tous les éléments dans le dossier dist/SidourAvoda
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SidourAvoda',
)

# Configuration pour macOS (optionnel, uniquement sur macOS)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='SidourAvoda.app',
        icon=icon_path,
        bundle_identifier='com.sidouravoda.app',
        info_plist={
            'CFBundleName': 'Sidour Avoda Pro',
            'CFBundleDisplayName': 'Sidour Avoda Pro',
            'CFBundleVersion': '1.0.48',
            'CFBundleShortVersionString': '1.0.48',
            'NSHighResolutionCapable': True,
        },
    )
