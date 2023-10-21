#!/bin/bash

# Define script and working directories
script_dir="/Users/sozeiga/Documents/Mac-Chrome"
working_dir="$script_dir/venv"

# Create a virtual environment named 'venv' in the script's directory (if it doesn't exist)
if [ ! -d "$working_dir" ]; then
    python3 -m venv "$working_dir"
fi

# Use the location of this script for other paths
BatchName="StartServer.sh"
batch_name="$script_dir/StartServer.sh" 
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

# Set the permissions for the plist file
chmod 644 "$plist_name"

# Load the plist into launchd
launchctl load "$plist_name"

# Upgrade pip and Install the necessary Python libraries
echo "Upgrading pip and Installing Python libraries..."
"$working_dir/bin/pip" install --only-binary Pillow Pillow
"$working_dir/bin/pip" install Flask flask-cors flask-socketio python-socketio[client] yt-dlp pymiere psutil Pillow pystray pygame
"$working_dir/bin/python" -m pip install --upgrade pip

# Install FFmpeg using Homebrew
echo "Installing FFmpeg using Homebrew..."
brew install ffmpeg

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
