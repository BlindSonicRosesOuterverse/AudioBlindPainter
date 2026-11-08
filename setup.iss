[Setup]
AppId={{B5F28B14-3C84-482F-9B67-C218B129E3AE}
AppName=AudioBlindPainter
AppVersion=1.0
AppPublisher=AudioBlindPainter Accessible Studio
DefaultDirName={autopf}\AudioBlindPainter
DisableDirPage=no
AppendDefaultDirName=yes
DefaultGroupName=AudioBlindPainter
DisableProgramGroupPage=no
OutputDir=.\InstallerOutput
OutputBaseFilename=AudioBlindPainter_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
ShowLanguageDialog=yes
WizardSizePercent=120

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"
Name: "pt"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Types]
Name: "full"; Description: "Full High-Contrast Installation (Recommended)"
Name: "custom"; Description: "Custom Installation (Choose Custom Drive/Folder)"; Flags: iscustom

[Components]
Name: "program"; Description: "Core Program Files (Required)"; Types: full custom; Flags: fixed
Name: "desktopicon"; Description: "Create high-contrast desktop shortcut"; Types: full
Name: "startmenuicon"; Description: "Create Start Menu shortcut and folder"; Types: full

[Files]
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: program
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: program

[Icons]
Name: "{group}\AudioBlindPainter"; Filename: "{app}\app.exe"; IconFilename: "{app}\icon.ico"; Components: startmenuicon
Name: "{group}\Uninstall AudioBlindPainter"; Filename: "{uninstallexe}"; Components: startmenuicon
Name: "{autodesktop}\AudioBlindPainter"; Filename: "{app}\app.exe"; IconFilename: "{app}\icon.ico"; Components: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "Launch AudioBlindPainter in High-Contrast Mode"; Flags: nowait postinstall skipifsilent
