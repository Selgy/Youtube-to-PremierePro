import os
import time
import winsound
import yt_dlp as youtube_dl
import pymiere
import sys
import socketio
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sio = socketio.Client()


def read_settings_from_local():
    try:
        settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
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

def sanitize_title(title):
    return (title.replace(":", " -")
                 .replace("|", "-")
                 .replace("：", " -")  
                 .replace("｜", "-"))  


def progress_hook(d):
    if d['status'] == 'downloading':
        percentage = d['_percent_str']
        print(f'Progress: {percentage}')  # Add this line
        sio.emit('percentage', {'percentage': percentage})  # emit the percentage update


def download_video(video_url, resolution, framerate, download_path):
    logging.info(f'Starting download of {video_url} with resolution {resolution}, framerate {framerate}, download path {download_path}')
    # Ensure download_path ends with a backslash
    download_path = os.path.join(download_path, '')


    with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
    
    video_title = sanitize_title(info_dict['title'])
    sanitized_output_template = f'{download_path}{video_title}.%(ext)s'

    ydl_opts = {
        'outtmpl': sanitized_output_template,
        'format': f'bestvideo[ext=mp4][vcodec*=avc1][height<={resolution}][fps<={framerate}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [progress_hook],
            'writesubtitles': False,
            'writeautomaticsub': False
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([video_url])


    # Check if the download was successful (result == 0)
    if result == 0:
        video_title = sanitize_title(info_dict['title'])  # Sanitizing title here
        video_filename = os.path.join(download_path, f"{video_title}.mp4")

        import_video_to_premiere(video_filename)
    else:
        logging.error(f'Failed to download video from {video_url}')

    if os.path.exists(video_filename):
        # Signal completion with a beep
        winsound.MessageBeep()
        time.sleep(2)  # This sleep is to delay the logging message, adjust as needed
        logging.info(f'Download and import completed successfully for {video_url}')
    else:
        logging.error("Video download failed.")


sio = socketio.Client()

if __name__ == "__main__":
    # Establish the Socket.IO connection at the beginning
    sio.connect('http://localhost:3000')

    settings = read_settings_from_local()
    if len(settings) != 3:
        logging.error("Error: Invalid settings format from the server.")
        sys.exit(1)

    resolution = settings['resolution']
    framerate = settings['framerate']
    download_path = settings['downloadPath']
    response = requests.get('http://localhost:3000/get-video-url')
    video_url = response.json()['videoUrl']
    if not video_url:
        logging.error('No video URL received from server')
        sys.exit(1)

    download_video(video_url, resolution, framerate, download_path)
    logging.info('Download completed')

    # Emit the import event
    sio.emit('import', download_path)
    # Disconnect from the server
    sio.disconnect()
