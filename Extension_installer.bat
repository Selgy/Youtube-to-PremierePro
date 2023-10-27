@echo off
setlocal

:: Path to your Python script
set "PythonScriptPath=%~dp0Youtube-download.py"

:: Use the location of this batch file for other paths
set "BatchName=StartServer.bat"

:: Change directory to the location of the batch file
cd /d %~dp0

:: Create a virtual environment named 'venv' in the current directory
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Now the commands will use the Python interpreter and pip from the virtual environment

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install the necessary Python libraries
echo Installing Python libraries...
pip install --only-binary Pillow Pillow
pip install Flask flask-cors flask-socketio python-socketio[client] yt-dlp pymiere psutil Pillow pystray pygame

:: Create a batch file to run Youtube-download.py
echo Creating batch file to run Python script...
echo @echo off > "%~dp0%BatchName%"
echo start "" "venv\Scripts\pythonw.exe" "%PythonScriptPath%" >> "%~dp0%BatchName%"

:: Define the path to the startup folder and the shortcut
set "StartupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ShortcutName=%StartupFolder%\StartServer.lnk"

:: Use PowerShell to create the shortcut
echo Creating shortcut to start server...
powershell -command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%ShortcutName%'); $s.TargetPath = '%~dp0%BatchName%'; $s.Save()"

:: Download FFmpeg
echo Downloading FFmpeg...
curl -L -o %TEMP%\ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2023-10-13-18-10/ffmpeg-n6.0-36-gc5039e158d-win64-gpl-6.0.zip

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
