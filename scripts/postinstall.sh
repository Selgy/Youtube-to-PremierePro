#!/bin/bash

# Define the Adobe CEP extensions directory for the current user
CEP_EXTENSIONS_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions"

# GitHub URL of the PymiereLink folder
GITHUB_REPO_URL="https://github.com/Selgy/Youtube-to-PremierePro/archive/Pre-released.zip"

# Path to the executable (update this with the actual path)
EXECUTABLE_PATH="/Applications/YoutubetoPremiere"

# Create the target directory if it doesn't exist
mkdir -p "$CEP_EXTENSIONS_DIR"

# Download PymiereLink folder from GitHub
echo "Downloading PymiereLink from GitHub..."
curl -L "$GITHUB_REPO_URL" --output "$CEP_EXTENSIONS_DIR/PymiereLink.zip"

# Unzip and move to the Adobe CEP extensions directory
echo "Installing PymiereLink..."
unzip -o "$CEP_EXTENSIONS_DIR/PymiereLink.zip" -d "$CEP_EXTENSIONS_DIR"
mv "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released/PymiereLink" "$CEP_EXTENSIONS_DIR/PymiereLink"
rm -rf "$CEP_EXTENSIONS_DIR/Youtube-to-PremierePro-Pre-released"
rm "$CEP_EXTENSIONS_DIR/PymiereLink.zip"

# Create the 'exec' directory inside PymiereLink
EXEC_DIR="$CEP_EXTENSIONS_DIR/PymiereLink/exec"
mkdir -p "$EXEC_DIR"

# Copy the executable to the 'exec' directory
echo "Copying executable to PymiereLink/exec..."
cp "$EXECUTABLE_PATH" "$EXEC_DIR"

if [ -f "$EXEC_DIR/$(basename "$EXECUTABLE_PATH")" ]; then
    echo "PymiereLink installed successfully."
else
    echo "Error: Failed to copy the executable."
    exit 1
fi
