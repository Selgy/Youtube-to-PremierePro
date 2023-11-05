# settings.py

# Basic settings
title = "YoutubetoPremiere"  # The title of the DMG window and the name of the resulting disk image
volume_icon = "icon.icns"  # The icon for the disk image
format = "UDBZ"  # The format of the disk image (UDRW, UDRO, UDCO, UDTO, UFBI, UDZO, UDBZ, ULFO)
size = None  # The size of the disk image (None for automatic sizing)
files = ["YoutubetoPremiere.app"]  # The files to include in the disk image
symlinks = {"Applications": "/Applications"}  # The symbolic links to include in the disk image

# Appearance
window_rect = ((400, 400), (500, 300))  # The size and position of the DMG window
default_view = "icon-view"  # The default view style for the DMG window (icon-view or list-view)
icon_size = 128  # The size of the icons in the DMG window
text_size = 16  # The size of the text in the DMG window
