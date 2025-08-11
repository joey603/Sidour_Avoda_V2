[Setup]
AppName=Sidour Avoda
AppVersion=1.0.0
DefaultDirName={pf}\Sidour Avoda
DefaultGroupName=Sidour Avoda
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=dist_installer
OutputBaseFilename=Sidour-Avoda-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Files]
; Sortie PyInstaller attendue dans le même dossier que ce script
Source: "dist\Sidour Avoda\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\dist\Sidour Avoda'))

[Icons]
Name: "{group}\Sidour Avoda"; Filename: "{app}\Sidour Avoda.exe"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\Sidour Avoda.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
Filename: "{app}\\Sidour Avoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait postinstall skipifsilent


