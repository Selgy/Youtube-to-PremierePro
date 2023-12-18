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
sudo mv "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released/com.selgy.youtubetopremiere" "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere" && echo "Move successful." || { echo "Failed to move directory"; exit 1; }
sudo rm -rf "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released"
sudo rm "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip"

EXEC_DIR="$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere/exec"
echo "Creating $EXEC_DIR..."
sudo mkdir -p "$EXEC_DIR" && echo "Exec directory created successfully." || { echo "Failed to create $EXEC_DIR"; exit 1; }

echo "Copying executable to $EXEC_DIR..."
sudo cp "$EXECUTABLE_PATH" "$EXEC_DIR" && echo "Executable copied successfully." || { echo "Failed to copy executable"; exit 1; }

if [ -f "$EXEC_DIR/$(basename "$EXECUTABLE_PATH")" ]; then
    echo "com.selgy.youtubetopremiere installed successfully."
else
    echo "Error: Failed to copy the executable."
    exit 1
fi


echo "Cleanup completed."
