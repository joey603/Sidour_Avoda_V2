[Setup]
AppName=Sidour Avoda
AppVersion=1.0.0
; AppId fixe pour remplacer proprement les anciennes versions
AppId={{0F8D381B-6E4E-4E7D-B8F7-7C4E0B28B0B2}
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
#ifexist "assets\\app.ico"
SetupIconFile=assets\\app.ico
#else
#ifexist "..\\assets\\app.ico"
SetupIconFile=..\\assets\\app.ico
#endif
#endif

[Files]
; Sortie PyInstaller (nom sans espace): dist\SidourAvoda\*
; IMPORTANT: ne pas utiliser "Check" ici, sinon les fichiers ne seront pas copiés à l'installation
Source: "dist\SidourAvoda\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
Filename: "{app}\\SidourAvoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"


