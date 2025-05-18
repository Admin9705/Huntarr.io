#define MyAppName "Huntarr"
#define ReadVersionFile(str fileName) \
   Local[0] = FileOpen(fileName), \
   Local[1] = FileRead(Local[0]), \
   FileClose(Local[0]), \
   Local[1]

#define MyAppVersion ReadVersionFile("version.txt")
#define MyAppPublisher "Huntarr"
#define MyAppURL "https://github.com/plexguide/Huntarr.io"
#define MyAppExeName "Huntarr.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{22AE2CDB-5F87-4E42-B5C3-28E121D4BDFF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=.\installer
OutputBaseFilename=Huntarr_Setup
SetupIconFile=frontend\static\logo\huntarr.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableDirPage=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
CloseApplications=no
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1
Name: "installservice"; Description: "Install as Windows Service (Requires Administrator Access)"; GroupDescription: "Windows Service"; Flags: checkedonce
Name: "createshortcut"; Description: "Create 'Run Without Service' shortcut"; GroupDescription: "Fallback Options"; Flags: checkedonce

[Files]
Source: "dist\Huntarr\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Create empty config directories to ensure they exist with proper permissions
Source: "LICENSE"; DestDir: "{app}\config"; Flags: ignoreversion; AfterInstall: CreateConfigDirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; First, remove any existing service
Filename: "{app}\{#MyAppExeName}"; Parameters: "--remove-service"; Flags: runhidden; Check: IsAdminLoggedOn
; Wait a moment for the service to be properly removed
Filename: "{sys}\cmd.exe"; Parameters: "/c timeout /t 3"; Flags: runhidden
; Install the service
Filename: "{app}\{#MyAppExeName}"; Parameters: "--install-service"; Description: "Install Huntarr as a Windows Service"; Tasks: installservice; Flags: runhidden; Check: IsAdminLoggedOn
; Grant permissions to the config directory 
Filename: "{sys}\cmd.exe"; Parameters: "/c icacls ""{app}\config"" /grant Everyone:(OI)(CI)F"; Flags: runhidden shellexec; Check: IsAdminLoggedOn
; Start the service
Filename: "{sys}\net.exe"; Parameters: "start Huntarr"; Flags: runhidden; Tasks: installservice; Check: IsAdminLoggedOn
; Launch Huntarr
Filename: "http://localhost:9705"; Description: "Open Huntarr Web Interface"; Flags: postinstall shellexec nowait
; Create batch file to run Huntarr without service
Filename: "{sys}\cmd.exe"; Parameters: "/c echo @echo off > ""{app}\Run_Huntarr_No_Service.bat"" && echo cd /d ""{app}"" >> ""{app}\Run_Huntarr_No_Service.bat"" && echo python ""{app}\{#MyAppExeName}"" --no-service >> ""{app}\Run_Huntarr_No_Service.bat"""; Flags: runhidden; Tasks: createshortcut
; Create shortcut for the batch file
Filename: "{sys}\cmd.exe"; Parameters: "/c powershell -Command ""& {$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('{commondesktop}\\Huntarr (No Service).lnk'); $s.TargetPath = '{app}\\Run_Huntarr_No_Service.bat'; $s.IconLocation = '{app}\\{#MyAppExeName},0'; $s.Save()}"""; Flags: runhidden; Tasks: createshortcut
; Launch Huntarr directly if service installation skipped or failed
Filename: "{app}\{#MyAppExeName}"; Parameters: "--no-service"; Description: "Run Huntarr without service"; Flags: nowait postinstall skipifsilent; Check: not IsTaskSelected('installservice') or not IsAdminLoggedOn

[UninstallRun]
; Stop the service first
Filename: "{sys}\net.exe"; Parameters: "stop Huntarr"; Flags: runhidden
; Wait a moment for the service to stop
Filename: "{sys}\cmd.exe"; Parameters: "/c timeout /t 3"; Flags: runhidden
; Then remove it
Filename: "{app}\{#MyAppExeName}"; Parameters: "--remove-service"; Flags: runhidden

[Code]
procedure CreateConfigDirs;
begin
  // Create necessary directories with explicit permissions
  ForceDirectories(ExpandConstant('{app}\config\logs'));
  ForceDirectories(ExpandConstant('{app}\config\stateful'));
  ForceDirectories(ExpandConstant('{app}\config\user'));
end;

// Check for admin rights and warn user if they're not an admin
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  NonAdminWarningResult: Integer;
begin
  // Try to stop the service if it's already running
  Exec(ExpandConstant('{sys}\net.exe'), 'stop Huntarr', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  // Give it a moment to stop
  Sleep(2000);
  
  // Warn if user is not admin
  if not IsAdminLoggedOn then
  begin
    NonAdminWarningResult := MsgBox(
      'Huntarr is being installed without administrator privileges.' + #13#10 + #13#10 +
      'Some features (like installing as a Windows service) will not work.' + #13#10 +
      'The application will still function in non-service mode, but will not start automatically with Windows.' + #13#10 + #13#10 +
      'Would you like to continue with the limited installation?',
      mbConfirmation,
      MB_YESNO);
    
    if NonAdminWarningResult = IDNO then
    begin
      MsgBox(
        'Installation aborted. Please restart the installer with administrator privileges (right-click and select "Run as administrator").',
        mbInformation,
        MB_OK);
      Result := False;
      Exit;
    end;
  end;
  
  Result := True;
end;

// Update task selections based on admin status
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectTasks then
  begin
    // If not admin, disable service installation and select the no-service option
    if not IsAdminLoggedOn then
    begin
      WizardForm.TasksList.CheckItem(WizardForm.TasksList.Items.IndexOf('Install as Windows Service (Requires Administrator Access)'), False);
      WizardForm.TasksList.ItemEnabled[WizardForm.TasksList.Items.IndexOf('Install as Windows Service (Requires Administrator Access)')] := False;
      WizardForm.TasksList.CheckItem(WizardForm.TasksList.Items.IndexOf('Create ''Run Without Service'' shortcut'), True);
    end;
  end;
end;
