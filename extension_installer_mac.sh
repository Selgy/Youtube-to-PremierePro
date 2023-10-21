<<<<<<< HEAD
#!/bin/bash

# Define script and working directories
script_dir="/Users/sozeiga/Documents/Mac-Chrome"
working_dir="$script_dir/venv"

# Create a virtual environment named 'venv' in the script's directory (if it doesn't exist)
if [ ! -d "$working_dir" ]; then
    python3 -m venv "$working_dir"
fi
=======
#!/usr/bin/env bash

# Path to your Python script
PythonScriptPath="$(dirname "$0")/Youtube-download.py"
>>>>>>> parent of fe866dc (update)

# Use the location of this script for other paths
BatchName="StartServer.sh"

<<<<<<< HEAD
# Create a shell script to run Youtube-download.py
echo "#!/bin/bash" > "$batch_name"
echo "source \"$working_dir/bin/activate\"" >> "$batch_name"  # Activate the virtual environment
echo "python3 \"$script_dir/Youtube-download.py\" &" >> "$batch_name"
chmod +x "$batch_name"  # Make the script executable

# Define the path to the LaunchAgents folder and the .plist file
launch_agents_folder="$HOME/Library/LaunchAgents"
plist_name="$launch_agents_folder/com.startserver.plist"

# Create the directory if it doesn't exist
mkdir -p "$launch_agents_folder"

# Create a .plist file for autostart
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > "$plist_name"
echo "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">" >> "$plist_name"
echo "<plist version=\"1.0\">" >> "$plist_name"
echo "<dict>" >> "$plist_name"
echo "  <key>Label</key>" >> "$plist_name"
echo "  <string>com.startserver</string>" >> "$plist_name"
echo "  <key>ProgramArguments</key>" >> "$plist_name"
echo "  <array>" >> "$plist_name"
echo "    <string>$batch_name</string>" >> "$plist_name"
echo "  </array>" >> "$plist_name"
echo "  <key>RunAtLoad</key>" >> "$plist_name"
echo "  <true/>" >> "$plist_name"
echo "</dict>" >> "$plist_name"
echo "</plist>" >> "$plist_name"

*
# Upgrade pip and Install the necessary Python libraries
echo "Upgrading pip and Installing Python libraries..."
"$working_dir/bin/pip" install --only-binary Pillow Pillow
"$working_dir/bin/pip" install Flask flask-cors flask-socketio python-socketio[client] yt-dlp pymiere psutil Pillow pystray pygame
"$working_dir/bin/python" -m pip install --upgrade pip

# Install FFmpeg using Homebrew
echo "Installing FFmpeg using Homebrew..."
brew install ffmpeg
=======
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
>>>>>>> parent of fe866dc (update)

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
<<<<<<< HEAD
=======
rm -rf "$tempdir"
>>>>>>> parent of fe866dc (update)
