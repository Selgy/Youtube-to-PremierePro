!include "MUI2.nsh"
!include "LogicLib.nsh"
!addincludedir "C:\ProgramData\chocolatey\lib\NSIS\tools\NSIS\Include"
!include "nsProcess.nsh"

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
    # Check if YoutubetoPremiere.exe is running
    ${ProcessExists} "YoutubetoPremiere.exe" $0
    ${If} $0 == 1
        MessageBox MB_OK|MB_ICONSTOP 'YoutubetoPremiere is currently running. Please close it before continuing.'
        Abort
    ${EndIf}

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
