# settings.py for dmgbuild

# Basic settings
title = "YoutubetoPremiere"  # The title of the DMG window and the name of the resulting disk image
size = None  # Size of the disk image (None for automatic sizing)
icon = "icon.icns"  # Icon for the DMG itself, should be a path relative to this script
background = None  # Background image for the DMG window (optional)

# Files to include
files = ["dist/YoutubetoPremiere.app"]  # The application to include in the DMG
symlinks = {"Applications": "/Applications"}  # Create a symlink to the Applications folder

# DMG window layout
window_rect = ((100, 100), (640, 280))  # Position and size of the DMG window
default_view = "icon-view"  # Default view style (icon-view or list-view)

# Icon size and positions in the DMG window
icon_size = 128
icon_locations = {
    "YoutubetoPremiere.app": (160, 120),
    "Applications": (480, 120),
}

# Text size (optional, for list-view mode)
text_size = 12