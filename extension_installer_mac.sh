#!/usr/bin/env bash

# Path to your Python script
PythonScriptPath="$(dirname "$0")/Youtube-download.py"

# Use the location of this script for other paths
BatchName="StartServer.sh"

# Create a script to run Youtube-download.py
echo "#!/bin/bash" > "$BatchName"
echo "pythonw \"$PythonScriptPath\" &" >> "$BatchName"
chmod +x "$BatchName"  # Make the script executable

# Define the path to the startup folder and the shortcut
StartupFolder="$HOME/.config/autostart"
ShortcutName="$StartupFolder/StartServer.desktop"

# Create the startup folder if it doesn't exist
mkdir -p "$StartupFolder"

# Create a .desktop file to run the script at startup
echo "[Desktop Entry]" > "$ShortcutName"
echo "Type=Application" >> "$ShortcutName"
echo "Exec=$(pwd)/$BatchName" >> "$ShortcutName"
echo "Hidden=false" >> "$ShortcutName"
echo "NoDisplay=false" >> "$ShortcutName"
echo "X-GNOME-Autostart-enabled=true" >> "$ShortcutName"
echo "Name[en_US]=StartServer" >> "$ShortcutName"
echo "Name=StartServer" >> "$ShortcutName"
echo "Comment[en_US]=Start the server" >> "$ShortcutName"
echo "Comment=Start the server" >> "$ShortcutName"

# Auto install PymiereLink extension to Premiere on mac

# Get temp path
tempdir=$(mktemp -d)

# Download zxp (extension) file
echo "Download .zxp file"
url="https://raw.githubusercontent.com/qmasingarbe/pymiere/master/pymiere_link.zxp"
fname_zxp=$(basename "$url")
path_zxp="$tempdir/$fname_zxp"
curl "$url" --output "$path_zxp"

# Download ExManCmd (extension manager)
echo "Download ExManCmd"
url="https://download.macromedia.com/pub/extensionmanager/ExManCmd_mac.dmg"
fname_exman=$(basename "$url")
path_exman="$tempdir/$fname_exman"
curl "$url" --output "$path_exman"

# Mount ExManCmd DMG
mount_path="$tempdir/ExManCmdMount"
echo "Mount ExManCmd DMG: $path_exman to $mount_path"
hdiutil attach "$path_exman" -mountpoint $mount_path

# Install the .zxp file
exmancmd="$mount_path/Contents/MacOS/ExManCmd"
echo "Install zxp"
"$exmancmd" --install "$path_zxp"

# Clean up
echo "Unmount ExManCmd DMG"
hdiutil detach "$mount_path"
rm -rf "$tempdir"
