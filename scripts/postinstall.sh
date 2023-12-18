#!/bin/bash

# Define the Adobe CEP extensions directory for the current user
CEP_EXTENSIONS_DIR="/Library/Application Support/Adobe/CEP/extensions"

# GitHub URL of the com.selgy.youtubetopremiere folder
GITHUB_REPO_URL="https://github.com/Selgy/Youtube-to-PremierePro/archive/Pre-released.zip"

# Path to the executable (update this with the actual path)
EXECUTABLE_PATH="/Applications/YoutubetoPremiere"

# Create the target directory if it doesn't exist
echo "Creating $CEP_EXTENSIONS_DIR..."
sudo mkdir -p "$CEP_EXTENSIONS_DIR" || { echo "Failed to create $CEP_EXTENSIONS_DIR"; exit 1; }

# Download com.selgy.youtubetopremiere folder from GitHub
echo "Downloading com.selgy.youtubetopremiere from GitHub..."
sudo curl -L "$GITHUB_REPO_URL" --output "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" || { echo "Failed to download from GitHub"; exit 1; }

# Unzip and move to the Adobe CEP extensions directory
echo "Installing com.selgy.youtubetopremiere..."
sudo unzip -o "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" -d "$CEP_EXTENSIONS_DIR" || { echo "Unzip failed"; exit 1; }
sudo mv "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released/com.selgy.youtubetopremiere" "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere" || { echo "Failed to move directory"; exit 1; }
sudo rm -rf "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released"
sudo rm "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip"

# Create the 'exec' directory inside com.selgy.youtubetopremiere
EXEC_DIR="$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere/exec"
echo "Creating $EXEC_DIR..."
sudo mkdir -p "$EXEC_DIR" || { echo "Failed to create $EXEC_DIR"; exit 1; }

# Copy the executable to the 'exec' directory
echo "Copying executable to $EXEC_DIR..."
sudo cp "$EXECUTABLE_PATH" "$EXEC_DIR" || { echo "Failed to copy executable"; exit 1; }

# Verify if the executable was copied successfully
if [ -f "$EXEC_DIR/$(basename "$EXECUTABLE_PATH")" ]; then
    echo "com.selgy.youtubetopremiere installed successfully."
else
    echo "Error: Failed to copy the executable."
    exit 1
fi

# Deleting youtubetopremiere and com.selgy.youtubetopremiere from the application folder
echo "Deleting youtubetopremiere and com.selgy.youtubetopremiere from the application folder..."
sudo rm -rf "/Applications/YoutubetoPremiere" || { echo "Failed to delete /Applications/YoutubetoPremiere"; exit 1; }
sudo rm -rf "/Applications/com.selgy.youtubetopremiere" || { echo "Failed to delete /Applications/com.selgy.youtubetopremiere"; exit 1; }

echo "Cleanup completed."
