[Setup]
AppName=Sidour Avoda
AppVersion=1.0.0
DefaultDirName={pf}\Sidour Avoda
DefaultGroupName=Sidour Avoda
OutputDir=dist_installer
OutputBaseFilename=Sidour-Avoda-Setup
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=no

[Files]
Source: "dist\Sidour Avoda\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Sidour Avoda"; Filename: "{app}\Sidour Avoda.exe"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\Sidour Avoda.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
Filename: "{app}\\Sidour Avoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait postinstall skipifsilent

