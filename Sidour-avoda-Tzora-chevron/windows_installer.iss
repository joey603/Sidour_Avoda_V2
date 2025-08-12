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
Name: "{group}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
Filename: "{app}\\SidourAvoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"


