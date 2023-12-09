#!/bin/bash

# Define the Adobe CEP extensions directory for the current user
CEP_EXTENSIONS_DIR="/Library/Application Support/Adobe/CEP/extensions"

# Define the source directory of PymiereLink (relative to the installation path)
SOURCE_DIR="$1/Contents/Resources/PymiereLink"

# Check if the source directory exists
if [ -d "$SOURCE_DIR" ]; then
    # Create the target directory if it doesn't exist
    mkdir -p "$CEP_EXTENSIONS_DIR/PymiereLink"

    # Copy PymiereLink to the Adobe CEP extensions directory
    cp -R "$SOURCE_DIR" "$CEP_EXTENSIONS_DIR"

    echo "PymiereLink installed successfully."
else
    echo "Error: PymiereLink source directory not found."
    exit 1
fi