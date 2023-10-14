import os
import subprocess
import time
import winsound
import yt_dlp as youtube_dl
import pymiere
import sys
import socketio
import requests
import json
import logging
from pathlib import Path
import base64  # Import the base64 module
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sio = socketio.Client()

def read_settings_from_local():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        logging.info('Settings read from local file successfully')
        return settings
    except Exception as e:
        logging.error(f'Error reading settings: {e}')
        sys.exit(1)

def import_video_to_premiere(video_path):
    try:
        proj = pymiere.objects.app.project
        root_bin = proj.rootItem
        proj.importFiles([video_path], suppressUI=True, targetBin=root_bin, importAsNumberedStills=False)
        logging.info(f'Video imported to Premiere successfully: {video_path}')
    except Exception as e:
        logging.error(f'Error importing video: {e}')

def re_encode_to_avc1(video_path):
    try:
        output_path = video_path.replace('.mp4', '_reencoded.mp4')
        ffmpeg_path = 'ffmpeg.exe'  # Adjust path if necessary
        command = [ffmpeg_path, '-i', video_path, '-c:v', 'libx264', '-c:a', 'copy', output_path]
        subprocess.run(command, check=True)
        logging.info(f'Video re-encoded successfully: {output_path}')
        return output_path
    except Exception as e:
        logging.error(f'Error re-encoding video: {e}')

def check_video_codec(video_path):
    try:
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(command, text=True, capture_output=True)
        logging.info(f'Video codec checked successfully: {result.stdout.strip()}')
        return result.stdout.strip()
    except Exception as e:
        logging.error(f'Error checking video codec: {e}')

def download_video(video_url, resolution, framerate, download_path):
    logging.info(f'Starting download of {video_url} with resolution {resolution}, framerate {framerate}, download path {download_path}')
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'format': f'bestvideo[ext=mp4][vcodec*=avc1][height<={resolution}][fps<={framerate}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'nooverwrites': False,  # This will overwrite the video file if it already exists
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        ydl.download([video_url])

    # Check if the video was downloaded successfully
    video_filename = os.path.join(download_path, f"{info_dict['title']}.mp4")
    codec = check_video_codec(video_filename)
    if codec.lower() == 'vp9':
        video_filename = re_encode_to_avc1(video_filename)
    import_video_to_premiere(video_filename)  # Moved this line here, out of the if/else block

    if os.path.exists(video_filename):
        # Signal completion with a beep
        winsound.MessageBeep()
        time.sleep(5)
        logging.info(f'Download and import completed successfully for {video_url}')
    else:
        logging.error("Video download failed.")

if __name__ == "__main__":
    settings = read_settings_from_local()
    if len(settings) != 3:
        logging.error("Error: Invalid settings format from the server.")
        sys.exit(1)

    # Modify these lines to extract values from the settings dictionary
    resolution = settings['resolution']
    framerate = settings['framerate']
    download_path_encoded = settings['downloadPath']
    download_path = download_path_encoded.encode('cp1252').decode('utf-8')




    response = requests.get('http://localhost:3000/get-video-url')
    video_url = response.json()['videoUrl']
    if not video_url:
        logging.error('No video URL received from server')
        sys.exit(1)

    download_video(video_url, resolution, framerate, download_path)
    logging.info('Download completed')
    # After downloading the video, trigger the import function in Adobe Premiere Pro via Node.js server
    sio.connect('http://localhost:3000')
    sio.emit('import', str(download_path))
    sio.disconnect()
