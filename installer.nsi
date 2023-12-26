!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsProcess.nsh"

Var ChromeExtensionCheckbox

Name 'YoutubetoPremiere Installer'
OutFile 'YoutubetoPremiereInstaller.exe'
!define MUI_ICON 'icon.ico'
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Open the chrome extension"
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE 'English'

Function .onInit
    StrCpy $INSTDIR "$PROGRAMFILES64\Common Files\Adobe\CEP\extensions\com.selgy.youtubetopremiere"
    StrCpy $ChromeExtensionCheckbox 1
FunctionEnd

Section 'Install YoutubetoPremiere' SEC01
    nsProcess::_FindProcess "YoutubetoPremiere.exe"
    Pop $R0
    ${If} $R0 == 0
        MessageBox MB_OK|MB_ICONSTOP 'YoutubetoPremiere is currently running. Please close it before continuing.'
        Abort
    ${EndIf}

    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere\exec'
    File 'dist\YoutubetoPremiere.exe'
    Rename "$INSTDIR\uninstall.exe" "$INSTDIR\com.selgy.youtubetopremiere\exec\uninstall.exe"
    SetOutPath '$INSTDIR\com.selgy.youtubetopremiere'
    File /r 'ffmpeg\*.*'
    File /r 'com.selgy.youtubetopremiere\*.*'
    WriteUninstaller "$INSTDIR\com.selgy.youtubetopremiere\exec\uninstall.exe"
SectionEnd

Section 'Uninstall'
    Delete '$INSTDIR\com.selgy.youtubetopremiere\exec\YoutubetoPremiere.exe'
    Delete '$INSTDIR\com.selgy.youtubetopremiere\exec\uninstall.exe'
    RMDir /r '$INSTDIR\com.selgy.youtubetopremiere'
    DeleteRegKey HKLM 'Software\YoutubetoPremiere'
SectionEnd

Function un.onGUIEnd
    ${If} $ChromeExtensionCheckbox == 1
        ExecShell "open" "https://chromewebstore.google.com/detail/youtube-to-premiere-pro/lhoepckbiamgobehojaibapoddjpfmfo"
    ${EndIf}
FunctionEnd
