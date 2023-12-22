!include 'MUI2.nsh'
Name 'YoutubetoPremiere Installer'
OutFile 'YoutubetoPremiereInstaller.exe'
!define MUI_ABORTWARNING
!define MUI_ICON 'icon.ico'
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE 'English'

Function .onInit
    ReadRegStr $R0 HKLM 'Software\YoutubetoPremiere' 'InstallDir'
    ${If} $R0 != ''
        MessageBox MB_ICONSTOP 'YoutubetoPremiere is already installed. Please uninstall the existing version before continuing.'
        Quit
    ${EndIf}
    nsExec::ExecToStack 'tasklist | findstr /R /C:"YoutubetoPremiere.exe"'
    Pop $0
    Pop $1
    StrCmp $0 0 0 processRunning
    MessageBox MB_OK|MB_ICONEXCLAMATION 'Please close YoutubetoPremiere before continuing with the installation.'
    Abort
    processRunning:
FunctionEnd

Section 'MainSection' SEC01
    SetOutPath '$INSTDIR'
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere'
    File /r 'com.selgy.youtubetopremiere\*.*'
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere\exec'
    File 'dist\YoutubetoPremiere.exe'
    CreateDirectory '$INSTDIR\com.selgy.youtubetopremiere\exec\ffmpeg_win'
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere\exec\ffmpeg_win'
    File /r 'ffmpeg\ffmpeg_win\*.*'
    WriteUninstaller '$INSTDIR\Uninstall.exe'
SectionEnd

Section 'Uninstall'
    Delete '$INSTDIR\YoutubetoPremiere.exe'
    RMDir /r '$INSTDIR\com.selgy.youtubetopremiere'
    Delete '$INSTDIR\Uninstall.exe'
    RMDir '$INSTDIR'
SectionEnd

ShowInstDetails show
ShowUnInstDetails show
