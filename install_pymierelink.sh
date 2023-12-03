#!/bin/bash

# Define the source and target directories
SOURCE_DIR="$(dirname "$0")/PymiereLink"
TARGET_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions/PymiereLink"

# Ask for the administrator password upfront
sudo -v

# Copy PymiereLink to the target directory
if [ -d "$SOURCE_DIR" ]; then
    echo "Installing PymiereLink..."
    sudo cp -R "$SOURCE_DIR" "$TARGET_DIR"
    echo "Installation complete."
else
    echo "Error: PymiereLink not found."
    exit 1
fi