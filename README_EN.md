# YouTube to Premiere Pro Importer

Streamline your video editing workflow by enabling a direct import of YouTube videos into Adobe Premiere Pro with a simple click. This tool, through a combination of custom scripts and an Adobe extension, creates a seamless integration between YouTube and Premiere Pro to enhance productivity by reducing the manual steps of downloading and importing videos.

## Features
1. **Direct Import**: Import YouTube videos directly into Adobe Premiere Pro with a click.
2. **Easy Access**: A simple button on the YouTube UI triggers the import process.
3. **Real-Time Progress**: Monitor the download and import progress in real-time.
4. **Streamlined Workflow**: Aims to save time and enhance productivity in your video editing process.

## Installation

### Verification
- Download the [YoutubetoPremiere-WinInstaller.exe](https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V1/YoutubetoPremiere-WinInstaller.exe).
- Upon installation, a `StartServer` entry will be created in the Startup folder of Windows to ensure the server is launched automatically at boot up.
- You will find a system tray icon at the bottom right of your Windows taskbar which represents the server. You can exit the server anytime by right-clicking on this icon and selecting 'Exit'.
- If you wish to launch the server manually, you can do so by navigating to the installation directory of `YoutubetoPremiere` (usually `C:\Program Files (x86)\YoutubetoPremiere`) and running the `startserver.bat` file.
- After ensuring that the server is running, navigate to YouTube and you should see a 'Premiere Pro' button next to the share button on video pages.
- Click the 'Premiere Pro' button to start the import process, and ensure the video is imported into Adobe Premiere Pro.

### Browser Extension
- Download the `ChromeExtension` folder from the latest release on the project's release page.
- Open the Chrome browser, and navigate to `chrome://extensions/`.
- At the top-right corner, toggle on the `Developer mode`.
- Click `Load unpacked` and select the `ChromeExtension` folder from your computer, usually located in `C:\Program Files (x86)\YoutubetoPremiere\ChromeExtension`.

### Verification
- Navigate to YouTube and you should see a 'Premiere Pro' button next to the share button on video pages.
- Click the 'Premiere Pro' button to start the import process, and ensure the video is imported into Adobe Premiere Pro.

## Usage
1. Ensure the server script is running (it should start automatically upon Windows Starting).
2. Make sure Premiere pro is open.
3. Open YouTube in your browser.
4. Navigate to the video you wish to import.
5. Click the 'Premiere Pro' button to start the download and import process.
6. Monitor the progress on the button label.
7. Once the import is complete, check Adobe Premiere Pro for the imported video.
