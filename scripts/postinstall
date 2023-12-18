#!/bin/bash

CEP_EXTENSIONS_DIR="/Library/Application Support/Adobe/CEP/extensions"
GITHUB_REPO_URL="https://github.com/Selgy/Youtube-to-PremierePro/archive/Pre-released.zip"
EXECUTABLE_PATH="/Applications/YoutubetoPremiere"

echo "Creating $CEP_EXTENSIONS_DIR..."
sudo mkdir -p "$CEP_EXTENSIONS_DIR" && echo "Directory created successfully." || { echo "Failed to create $CEP_EXTENSIONS_DIR"; exit 1; }

echo "Downloading com.selgy.youtubetopremiere from GitHub..."
sudo curl -L "$GITHUB_REPO_URL" --output "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" && echo "Download successful." || { echo "Failed to download from GitHub"; exit 1; }

echo "Installing com.selgy.youtubetopremiere..."
sudo unzip -o "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" -d "$CEP_EXTENSIONS_DIR" && echo "Unzip successful." || { echo "Unzip failed"; exit 1; }

# Check if the directory already exists and remove it if necessary
if [ -d "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere" ]; then
    sudo rm -rf "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere"
fi

sudo mv "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released/com.selgy.youtubetopremiere" "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere" && echo "Move successful." || { echo "Failed to move directory"; exit 1; }

# Delete the downloaded ZIP file
sudo rm "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" && echo "ZIP file deleted successfully." || { echo "Failed to delete ZIP file"; exit 1; }

EXEC_DIR="$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere/exec"
echo "Creating $EXEC_DIR..."
sudo mkdir -p "$EXEC_DIR" && echo "Exec directory created successfully." || { echo "Failed to create $EXEC_DIR"; exit 1; }

echo "Copying executable to $EXEC_DIR..."
sudo cp -R "$EXECUTABLE_PATH/"* "$EXEC_DIR" && echo "Executable copied successfully." || { echo "Failed to copy executable"; exit 1; }

if [ -d "$EXEC_DIR/YoutubetoPremiere" ]; then
    echo "com.selgy.youtubetopremiere installed successfully."
else
    echo "Error: Failed to copy the executable."
fi

echo "Cleanup started..."

# Deleting YoutubetoPremiere and related files from the application folder
if [ -d "/Applications/YoutubetoPremiere" ]; then
    sudo rm -rf "/Applications/YoutubetoPremiere" && echo "Deleted /Applications/YoutubetoPremiere directory." || { echo "Failed to delete /Applications/YoutubetoPremiere"; exit 1; }
else
    echo "Directory /Applications/YoutubetoPremiere does not exist or already deleted."
fi

if [ -d "/Applications/com.selgy.youtubetopremiere" ]; then
    sudo rm -rf "/Applications/com.selgy.youtubetopremiere" && echo "Deleted /Applications/com.selgy.youtubetopremiere directory." || { echo "Failed to delete /Applications/com.selgy.youtubetopremiere"; exit 1; }
else
    echo "Directory /Applications/com.selgy.youtubetopremiere does not exist or already deleted."
fi

echo "Cleanup completed."
