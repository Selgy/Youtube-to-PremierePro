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

    # Create the uninstaller in the main installation directory
    WriteUninstaller "$INSTDIR\uninstall.exe"

    SetOutPath '$INSTDIR\exec'
    File 'dist\YoutubetoPremiere.exe'
    File 'ffmpeg/ffmpeg_win\*.*'
    Rename "$INSTDIR\uninstall.exe" "$INSTDIR\exec\uninstall.exe"
    
    SetOutPath '$INSTDIR'
    File /r 'com.selgy.youtubetopremiere\*.*'
SectionEnd

Section 'Uninstall'
    Delete '$INSTDIR\exec\YoutubetoPremiere.exe'
    Delete '$INSTDIR\exec\uninstall.exe'
    RMDir /r '$INSTDIR\exec\ffmpeg_win'
    RMDir /r '$INSTDIR'
    DeleteRegKey HKLM 'Software\YoutubetoPremiere'
SectionEnd

Function un.onGUIEnd
    ${If} $ChromeExtensionCheckbox == 1
        ExecShell "open" "https://chromewebstore.google.com/detail/youtube-to-premiere-pro/lhoepckbiamgobehojaibapoddjpfmfo"
    ${EndIf}
FunctionEnd
