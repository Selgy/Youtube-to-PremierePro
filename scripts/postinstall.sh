#!/bin/bash

# Define the Adobe CEP extensions directory for the current user
CEP_EXTENSIONS_DIR="/Library/Application Support/Adobe/CEP/extensions"

# GitHub URL of the com.selgy.youtubetopremiere folder
GITHUB_REPO_URL="https://github.com/Selgy/Youtube-to-PremierePro/archive/Pre-released.zip"

# Path to the executable (update this with the actual path)
EXECUTABLE_PATH="/Applications/YoutubetoPremiere"

# Create the target directory if it doesn't exist
mkdir -p "$CEP_EXTENSIONS_DIR"

# Download com.selgy.youtubetopremiere folder from GitHub
echo "Downloading com.selgy.youtubetopremiere from GitHub..."
curl -L "$GITHUB_REPO_URL" --output "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip"

# Unzip and move to the Adobe CEP extensions directory
echo "Installing com.selgy.youtubetopremiere..."
unzip -o "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip" -d "$CEP_EXTENSIONS_DIR"
mv "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released/com.selgy.youtubetopremiere" "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere"
rm -rf "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released"
rm "$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere.zip"

# Create the 'exec' directory inside com.selgy.youtubetopremiere
EXEC_DIR="$CEP_EXTENSIONS_DIR/com.selgy.youtubetopremiere/exec"
mkdir -p "$EXEC_DIR"

# Copy the executable to the 'exec' directory
echo "Copying executable to com.selgy.youtubetopremiere/exec..."
cp "$EXECUTABLE_PATH" "$EXEC_DIR"

if [ -f "$EXEC_DIR/$(basename "$EXECUTABLE_PATH")" ]; then
    echo "com.selgy.youtubetopremiere installed successfully."
else
    echo "Error: Failed to copy the executable."
    exit 1
fi

# Deleting youtubetopremiere and com.selgy.youtubetopremiere from the application folder
echo "Deleting youtubetopremiere and com.selgy.youtubetopremiere from the application folder..."
rm -rf "/Applications/youtubetopremiere"
rm -rf "/Applications/com.selgy.youtubetopremiere"

echo "Cleanup completed."
