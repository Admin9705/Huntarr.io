!include "MUI2.nsh"
!include "FileFunc.nsh"

# Define app name and version
!define APPNAME "Huntarr.io"
!define COMPANYNAME "PlexGuide"
!define DESCRIPTION "Automated media collection management"
!define VERSIONMAJOR 6
!define VERSIONMINOR 2
!define VERSIONBUILD 6
!define HELPURL "https://github.com/plexguide/Huntarr.io"
!define UPDATEURL "https://github.com/plexguide/Huntarr.io/releases"
!define ABOUTURL "https://github.com/plexguide/Huntarr.io"

# Installer configuration
Name "${APPNAME}"
OutFile "Huntarr-Setup-${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}" "InstallDir"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

# Include Modern UI
!define MUI_ICON "..\assets\huntarr.ico"
!define MUI_UNICON "..\assets\huntarr.ico"
!define MUI_ABORTWARNING

# Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

# Language
!insertmacro MUI_LANGUAGE "English"

# Components
Section "Huntarr Core" SecCore
  SectionIn RO # Required
  
  SetOutPath "$INSTDIR"
  
  # Copy main executable
  File "..\dist\Huntarr.exe"
  
  # Create data directories
  SetOutPath "$INSTDIR\config"
  File /nonfatal "..\config\config.template.json"
  
  # Create necessary directories
  CreateDirectory "$INSTDIR\config\logs"
  CreateDirectory "$INSTDIR\config\user"
  CreateDirectory "$INSTDIR\config\state"
  CreateDirectory "$INSTDIR\config\stateful"
  
  # Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\Huntarr.exe"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  # Create desktop shortcut
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\Huntarr.exe"
  
  # Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  # Write registry keys for Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\Huntarr.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
  
  # Get installed size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

Section "Windows Service" SecService
  # Install as Windows service
  DetailPrint "Installing Huntarr as a Windows service..."
  ExecWait '"$INSTDIR\Huntarr.exe" --install-service'
  
  # Set service to auto-start
  DetailPrint "Configuring service to start automatically..."
  ExecWait 'sc config "Huntarr" start=auto'
  
  # Start the service
  DetailPrint "Starting Huntarr service..."
  ExecWait 'sc start "Huntarr"'
  
  # Provide feedback about service installation
  DetailPrint "Huntarr service has been installed and started."
SectionEnd

Section "Desktop Shortcut" SecDesktop
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\Huntarr.exe"
SectionEnd

# Component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core Huntarr application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecService} "Install Huntarr as a Windows service (runs automatically in the background)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcut"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

# Uninstaller
Section "Uninstall"
  # Stop and remove service if installed
  DetailPrint "Stopping Huntarr service..."
  ExecWait 'sc stop "Huntarr"'
  
  DetailPrint "Removing Huntarr service..."
  ExecWait '"$INSTDIR\Huntarr.exe" --remove-service'
  ExecWait 'sc delete "Huntarr"'
  
  # Remove files
  Delete "$INSTDIR\Huntarr.exe"
  Delete "$INSTDIR\Uninstall.exe"
  
  # Remove shortcuts
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\*.*"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  # Ask if user wants to remove config files
  MessageBox MB_YESNO|MB_ICONQUESTION "Would you like to keep your Huntarr configuration files? Click Yes to keep config files, No to remove them." IDYES KeepConfig
    # Remove config directories
    RMDir /r "$INSTDIR\config"
    DetailPrint "Configuration files removed."
    Goto ConfigDone
  KeepConfig:
    DetailPrint "Configuration files preserved."
  ConfigDone:

  # Remove install directory (if empty)
  RMDir "$INSTDIR"
  
  # Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  DeleteRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}"
  
  DetailPrint "Huntarr has been uninstalled."
SectionEnd