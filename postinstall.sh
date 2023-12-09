#!/bin/bash

# Define the Adobe CEP extensions directory
CEP_EXTENSIONS_DIR="$HOME/Library/Application Support/Adobe/CEP/extensions"

# Define the source directory of PymiereLink (adjust this path as needed)
SOURCE_DIR="$1/Contents/Resources/PymiereLink"

# Create the target directory if it doesn't exist
mkdir -p "$CEP_EXTENSIONS_DIR"

# Copy PymiereLink to the Adobe CEP extensions directory
cp -R "$SOURCE_DIR" "$CEP_EXTENSIONS_DIR/PymiereLink"