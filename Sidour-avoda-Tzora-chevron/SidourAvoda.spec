# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('planning_data.db', '.'),
        ('assets/calender-2389150_960_720.png', 'assets'),
        ('assets/app.ico', 'assets'),
        ('version.txt', '.'),
        ('interface.py', '.'),
        ('interface_2.py', '.'),
        ('planning.py', '.'),
        ('database.py', '.'),
        ('horaire.py', '.'),
        ('travailleur.py', '.'),
    ],
    hiddenimports=[
        'interface',
        'planning', 
        'database',
        'horaire',
        'travailleur',
        'tkinter',
        'tkinter.ttk',
        'ttkbootstrap',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico',
)

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
