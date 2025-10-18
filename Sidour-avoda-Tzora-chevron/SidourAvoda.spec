# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('version.txt','.'), ('interface_2.py','.'), ('coach_marks.py','.')],
    hiddenimports=['interface', 'interface_2', 'coach_marks', 'planning', 'database', 'horaire', 'travailleur', 'tkinter', 'tkinter.ttk', 'ttkbootstrap'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    icon=['assets/app.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SidourAvoda',
)
app = BUNDLE(
    coll,
    name='SidourAvoda.app',
    icon='assets/app.icns',
    bundle_identifier=None,
)
