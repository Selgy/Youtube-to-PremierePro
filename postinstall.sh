#!/bin/bash

# Check if Homebrew is installed
if ! command -v brew &>/dev/null; then
    echo "Homebrew is not installed. Please install Homebrew first."
    exit 1
fi

# Update Homebrew and upgrade any already-installed formulae
brew update
brew upgrade
brew install python@3.8
brew install gettext

# Define the Adobe CEP extensions directory for the current user
CEP_EXTENSIONS_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions"

# Define the source directory of PymiereLink
SOURCE_DIR="/Applications/Youtubetopremiere.app/Contents/Resources/PymiereLink"

# Create the target directory if it doesn't exist
mkdir -p "$CEP_EXTENSIONS_DIR/PymiereLink"

# Copy PymiereLink to the Adobe CEP extensions directory (including subdirectories)
if cp -R "$SOURCE_DIR"/* "$CEP_EXTENSIONS_DIR/PymiereLink"; then
    echo "PymiereLink installed successfully."
else
    echo "Error: Failed to copy PymiereLink."
    exit 1
fi
