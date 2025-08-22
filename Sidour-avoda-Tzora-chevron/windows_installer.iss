#ifndef MyVersion
#define MyVersion "v0.0.0"
#endif

#ifexist "dist\\SidourAvoda\\SidourAvoda.exe"
#define DistDir "dist\\SidourAvoda"
#else
#ifexist "..\\dist\\SidourAvoda\\SidourAvoda.exe"
#define DistDir "..\\dist\\SidourAvoda"
#else
#ifexist "Sidour-avoda-Tzora-chevron\\dist\\SidourAvoda\\SidourAvoda.exe"
#define DistDir "Sidour-avoda-Tzora-chevron\\dist\\SidourAvoda"
#else
#error "No PyInstaller dist found (expected dist\\SidourAvoda, ..\\dist\\SidourAvoda, or Sidour-avoda-Tzora-chevron\\dist\\SidourAvoda). Build step must run before packaging."
#endif
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
; Exclure l'exe de base du bulk, on le copie explicitement juste après
Source: "{#DistDir}\*"; DestDir: "{app}"; Excludes: "SidourAvoda.exe"; Flags: recursesubdirs createallsubdirs
; Copier l'exe en deux variantes: stable (non versionné) et versionnée
Source: "{#DistDir}\SidourAvoda.exe"; DestDir: "{app}"; DestName: "SidourAvoda.exe"; Flags: ignoreversion replacesameversion
Source: "{#DistDir}\SidourAvoda.exe"; DestDir: "{app}"; DestName: "SidourAvoda-{#MyVersion}.exe"; Flags: ignoreversion replacesameversion

[InstallDelete]
; Ne plus supprimer les exécutables versionnés à l'installation pour éviter les raccourcis cassés
; Supprimer les anciens raccourcis potentiellement cassés avant de recréer ceux pointant vers l'exe stable
Type: files; Name: "{group}\\Sidour Avoda*.lnk"
Type: files; Name: "{userdesktop}\\Sidour Avoda*.lnk"
Type: files; Name: "{commondesktop}\\Sidour Avoda*.lnk"
; Supprimer toutes les anciennes versions d'exécutables versionnés (seront remplacées ensuite)
Type: files; Name: "{app}\\SidourAvoda-v*.exe"

[UninstallDelete]
; Nettoyage également à la désinstallation
Type: files; Name: "{app}\\SidourAvoda-v*.exe"

[Icons]
; Pointer les raccourcis vers l'exécutable stable non versionné pour rester valides après mise à jour
Name: "{group}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; WorkingDir: "{app}"; IconIndex: 0
Name: "{userdesktop}\Sidour Avoda"; Filename: "{app}\SidourAvoda.exe"; Tasks: desktopicon; WorkingDir: "{app}"; IconIndex: 0

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis:"

[Run]
; Lancer l'exécutable stable non versionné
Filename: "{app}\\SidourAvoda.exe"; Description: "Lancer Sidour Avoda"; Flags: nowait runasoriginaluser; WorkingDir: "{app}"
; Rafraîchir le cache d'icônes de l'utilisateur pour que le raccourci affiche l'icône immédiatement
Filename: "{sys}\\ie4uinit.exe"; Parameters: "-show"; Flags: runasoriginaluser


