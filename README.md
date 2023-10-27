# YouTube to Premiere Pro Importer

Streamline your video editing workflow by enabling a direct import of YouTube videos into Adobe Premiere Pro with a simple click. This tool, through a combination of custom scripts and an Adobe extension, creates a seamless integration between YouTube and Premiere Pro to enhance productivity by reducing the manual steps of downloading and importing videos.

## Features
1. **Direct Import**: Import YouTube videos directly into Adobe Premiere Pro with a click.
2. **Easy Access**: A simple button on the YouTube UI triggers the import process.
3. **Real-Time Progress**: Monitor the download and import progress in real-time.
4. **Cross-Platform**: Compatible with both Windows and MacOS.
5. **Streamlined Workflow**: Aims to save time and enhance productivity in your video editing process.

## Installation
### Browser Extension
- Download the `ChromeExtension` folder from the latest release on the project's release page.
- Open the Chrome browser, and navigate to `chrome://extensions/`.
- At the top-right corner, toggle on the `Developer mode`.
- Click `Load unpacked` and select the `ChromeExtension` folder from your computer, usually located in `C:\Program Files (x86)\YoutubetoPremiere\ChromeExtension`.

### Server and Pymiere Extension
- Download the latest release of this project for your operating system from the releases page.
- Extract the downloaded zip file.
- Run the provided `.bat` file (for Windows) or `.sh` file (for MacOS) to install the server and the Pymiere extension.

### Verification
- Navigate to YouTube and you should see a 'Premiere Pro' button next to the share button on video pages.
- Click the 'Premiere Pro' button to start the import process, and ensure the video is imported into Adobe Premiere Pro.

## Usage
1. Ensure the server script is running (it should start automatically upon installation).
2. Open YouTube in your browser.
3. Navigate to the video you wish to import.
4. Click the 'Premiere Pro' button to start the download and import process.
5. Monitor the progress on the button label.
6. Once the import is complete, check Adobe Premiere Pro for the imported video.
