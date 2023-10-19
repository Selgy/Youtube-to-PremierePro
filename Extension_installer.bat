@echo off
setlocal

:: Path to your Python script
set "PythonScriptPath=%~dp0Youtube-download.py"

:: Use the location of this batch file for other paths
set "BatchName=StartServer.bat"

:: Create a batch file to run Youtube-download.py
echo @echo off > "%~dp0%BatchName%"
echo start "" "pythonw" "%PythonScriptPath%" >> "%~dp0%BatchName%"

:: Define the path to the startup folder and the shortcut
set "StartupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ShortcutName=%StartupFolder%\StartServer.lnk"

:: Use PowerShell to create the shortcut
powershell -command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%ShortcutName%'); $s.TargetPath = '%~dp0%BatchName%'; $s.Save()"

:: Auto install PymiereLink extension to Premiere on windows
echo Downloading Adobe Extension Manager
curl "http://download.macromedia.com/pub/extensionmanager/ExManCmd_win.zip" --output %temp%\ExManCmd_win.zip
echo.

echo Download PymiereLink extension
curl "https://raw.githubusercontent.com/qmasingarbe/pymiere/master/pymiere_link.zxp" --output %temp%\pymiere_link.zxp
echo.

echo Unzip Extension Manager
rem require powershell
powershell Expand-Archive %temp%\ExManCmd_win.zip -DestinationPath %temp%\ExManCmd_win -Force
echo.

echo Install Extension
call %temp%\ExManCmd_win\ExManCmd.exe /install %temp%\pymiere_link.zxp
if %ERRORLEVEL% NEQ 0 (
    echo Installation failed...
) else (
    echo.
    echo Installation successful !
)

endlocal