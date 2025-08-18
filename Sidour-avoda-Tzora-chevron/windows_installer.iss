#ifndef MyVersion
#define MyVersion "v0.0.0"
#endif

#ifexist "dist\\SidourAvoda\\SidourAvoda.exe"
#define DistDir "dist\\SidourAvoda"
#else
#ifexist "..\\dist\\SidourAvoda\\SidourAvoda.exe"
#define DistDir "..\\dist\\SidourAvoda"
#else
#error "No PyInstaller dist found (expected dist\\SidourAvoda or ..\\dist\\SidourAvoda). Build step must run before packaging."
#endif
#endif

[Setup]
AppName=Sidour Avoda
AppVersion={#MyVersion}
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
; Fermer les applis ouvertes et les relancer après install
CloseApplications=yes
RestartApplications=yes
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
; Exclure l'exe de base pour le renommer en versionné
Source: "{#DistDir}\*"; DestDir: "{app}"; Excludes: "SidourAvoda.exe"; Flags: recursesubdirs createallsubdirs
; Copier l'exe et le renommer avec la version (incluant le v)
Source: "{#DistDir}\SidourAvoda.exe"; DestDir: "{app}"; DestName: "SidourAvoda-{#MyVersion}.exe"; Flags: ignoreversion replacesameversion

[InstallDelete]
; Nettoyage d'anciens exécutables versionnés dans le dossier d'installation
Type: files; Name: "{app}\\SidourAvoda-v*.exe"

[UninstallDelete]
; Nettoyage également à la désinstallation
Type: files; Name: "{app}\\SidourAvoda-v*.exe"

[Icons]
Name: "{group}\Sidour Avoda"; Filename: "{app}\SidourAvoda-{#MyVersion}.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\SidourAvoda-{#MyVersion}.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
; Lancer l'application versionnée même en mode silencieux et sous l'utilisateur original
Filename: "{app}\\SidourAvoda-{#MyVersion}.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait runasoriginaluser; WorkingDir: "{app}"


