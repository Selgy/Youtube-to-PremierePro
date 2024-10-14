!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsProcess.nsh"

Var ChromeExtensionCheckbox

Name 'YoutubetoPremiere Installer'
OutFile 'YoutubetoPremiere_Win.exe'
!define MUI_ICON 'icon.ico'
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME "https://chromewebstore.google.com/u/3/detail/youtube-to-premiere-pro-v/fnhpeiohcfobchjffmgfdeobphhmaibb?hl=fr"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Open Chrome Extension Page"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE 'English'

Function .onInit
    StrCpy $INSTDIR "$PROGRAMFILES64\Common Files\Adobe\CEP\extensions\com.selgy.youtubetopremiere"
    StrCpy $ChromeExtensionCheckbox 1 ; Set to 1 to be checked by default
FunctionEnd

Section 'Install YoutubetoPremiere' SEC01
    nsProcess::_FindProcess "YoutubetoPremiere.exe"
    Pop $R0
    ${If} $R0 == 0
        MessageBox MB_OK|MB_ICONSTOP 'YoutubetoPremiere is currently running. Please close it before continuing.'
        Abort
    ${EndIf}



    SetOutPath '$INSTDIR\exec'
    File 'dist\YoutubetoPremiere.exe'
    
    SetOutPath '$INSTDIR\exec\ffmpeg_win'
    File /r 'ffmpeg_win\*.*'
    
    SetOutPath '$INSTDIR'
    File /r 'com.selgy.youtubetopremiere\*.*'
SectionEnd

Section "Enable Debugging for CSXS Versions 6 to 11"
    WriteRegStr HKCU "Software\Adobe\CSXS.6" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.7" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.8" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.9" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.10" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.11" "PlayerDebugMode" "1"
    WriteRegStr HKCU "Software\Adobe\CSXS.12" "PlayerDebugMode" "1"
SectionEnd

Section 'Uninstall'
    Delete '$INSTDIR\exec\YoutubetoPremiere.exe'
    Delete '$INSTDIR\exec\uninstall.exe'
    RMDir /r '$INSTDIR\exec\ffmpeg_win'
    RMDir /r '$INSTDIR'
    DeleteRegKey HKLM 'Software\YoutubetoPremiere'
SectionEnd

Function un.onGUIEnd
    ; No need for ExecShell command here
FunctionEnd
