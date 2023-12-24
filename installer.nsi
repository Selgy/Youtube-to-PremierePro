!include MUI2.nsh
Name 'YoutubetoPremiere Installer'
OutFile 'YoutubetoPremiereInstaller.exe'
!define MUI_ICON 'icon.ico'
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE 'English'

Function .onInit
    # Set the installation path
    StrCpy $INSTDIR "$PROGRAMFILES64\Common Files\Adobe\CEP\extensions\com.selgy.youtubetopremiere"
FunctionEnd

Section 'Install YoutubetoPremiere' SEC01
    nsExec::ExecToStack 'tasklist /nh /fi "imagename eq YoutubetoPremiere.exe"'
    Pop $0
    Pop $1
    StrCmp $1 '' installationContinue
    StrCmp $1 'INFO: No tasks are running.' installationContinue
    MessageBox MB_OK|MB_ICONSTOP 'YoutubetoPremiere is currently running. Please close it before continuing.'
    Abort
    installationContinue:
    SetOutPath '$INSTDIR'
    File 'dist\YoutubetoPremiere.exe'
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere\exec'
    File /r 'ffmpeg\*.*'
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere'
    File /r 'com.selgy.youtubetopremiere\*.*'
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section 'Uninstall'
    Delete '$INSTDIR\YoutubetoPremiere.exe'
    RMDir /r '$INSTDIR\com.selgy.youtubetopremiere\exec\ffmpeg_win'
    RMDir /r '$INSTDIR\com.selgy.youtubetopremiere'
    DeleteRegKey HKLM 'Software\YoutubetoPremiere'
SectionEnd
