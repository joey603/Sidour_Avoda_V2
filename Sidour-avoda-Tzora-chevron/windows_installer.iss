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
; Sortie PyInstaller (nom sans espace): dist\SidourAvoda\*
Source: "dist\SidourAvoda\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\dist\SidourAvoda'))

[Icons]
Name: "{group}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
Filename: "{app}\\SidourAvoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait postinstall skipifsilent


