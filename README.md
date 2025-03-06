# Sidour-avoda-Tzora-chevron

## Description
Sidour-avoda-Tzora-chevron is a schedule management application for organizing shifts and work hours. It allows you to create, manage, and optimize worker schedules while respecting various constraints such as minimum rest time between shifts.

## Main Features
- Adding and managing workers
- Automatic generation of optimized schedules
- Verification of minimum rest between shifts (8 hours by default)
- Clear schedule visualization
- Manual assignment modifications
- Evaluation of generated schedule quality
- Saving and loading schedules
- Exporting schedules to CSV format

## Schedule Structure
The application manages three daily time slots:
- Morning: 06:00-14:00
- Afternoon: 14:00-22:00
- Night: 22:00-06:00

## Installation
1. Make sure you have Python installed on your system
2. Clone this repository:
   ```
   git clone https://github.com/your-username/Sidour-avoda-Tzora-chevron.git
   cd Sidour-avoda-Tzora-chevron
   ```
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To launch the application, run:
```

The graphical interface will allow you to:
1. Add workers with their constraints
2. Automatically generate optimized schedules
3. Visualize and modify schedules
4. Save and load existing schedules
5. Export schedules to CSV format

## Customizable Parameters
- Minimum rest between shifts (8 hours by default)
- Worker-specific constraints
- Schedule preferences

## Advanced Features
- 12-hour schedule generation
- Automatic gap filling in the schedule
- Evaluation of night shift distribution
- Management of closely scheduled shifts

## Building a Standalone Application

### Prerequisites
- Python 3.6 or higher
- PyInstaller (install with `pip install pyinstaller`)
- Required dependencies (install with `pip install -r requirements.txt`)

### Building on macOS
1. Make sure all dependencies are installed:
   ```
   pip install pyinstaller
   pip install -r requirements.txt
   ```

2. Create a spec file for the application:
   ```
   cd Sidour-avoda-Tzora-chevron
   ```

3. Create or modify the `macos_app.spec` file with the following content:
   ```python
   # -*- mode: python ; coding: utf-8 -*-

   block_cipher = None

   a = Analysis(
       ['main.py'],
       pathex=[],
       binaries=[],
       datas=[
           ('assets/calender-2389150_960_720.png', 'assets'),
           ('planning_data.db', '.')
       ],
       hiddenimports=[],
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
       name='Sidour Avoda',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       console=False,
       disable_windowed_traceback=False,
       argv_emulation=True,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
       icon='assets/calender-2389150_960_720.png',
   )
   coll = COLLECT(
       exe,
       a.binaries,
       a.zipfiles,
       a.datas,
       strip=False,
       upx=True,
       upx_exclude=[],
       name='Sidour Avoda',
   )
   app = BUNDLE(
       coll,
       name='Sidour Avoda.app',
       icon='assets/calender-2389150_960_720.png',
       bundle_identifier='com.sidouravoda.app',
       info_plist={
           'CFBundleShortVersionString': '1.0.0',
           'NSHighResolutionCapable': 'True',
           'NSPrincipalClass': 'NSApplication',
           'NSAppleScriptEnabled': False,
           'LSBackgroundOnly': False,
           'LSUIElement': False,
       },
   )
   ```

4. Build the application:
   ```
   pyinstaller macos_app.spec
   ```

5. The standalone application will be created in the `dist` folder as `Sidour Avoda.app`

### Building on Windows
1. Install required dependencies:
   ```
   pip install pyinstaller
   pip install -r requirements.txt
   ```

2. Create a spec file for Windows:
   ```
   cd Sidour-avoda-Tzora-chevron
   ```

3. Create or modify the `windows_app.spec` file with the following content:
   ```python
   # -*- mode: python ; coding: utf-8 -*-

   block_cipher = None

   a = Analysis(
       ['main.py'],
       pathex=[],
       binaries=[],
       datas=[
           ('assets/calender-2389150_960_720.png', 'assets'),
           ('planning_data.db', '.')
       ],
       hiddenimports=[],
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
       a.binaries,
       a.zipfiles,
       a.datas,
       [],
       name='Sidour Avoda',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       upx_exclude=[],
       runtime_tmpdir=None,
       console=False,
       disable_windowed_traceback=False,
       argv_emulation=False,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
       icon='assets/calender-2389150_960_720.png',
   )
   ```

4. Build the application:
   ```
   pyinstaller windows_app.spec
   ```

5. The standalone application will be created in the `dist` folder as `Sidour Avoda.exe`

### Troubleshooting
- If the application crashes on startup, check the error log at `~/sidour_avoda_error.log`
- Make sure all required files are included in the spec file
- For database issues, ensure the database file is properly included and accessible
- If you encounter permission issues, try running the build command with administrator privileges