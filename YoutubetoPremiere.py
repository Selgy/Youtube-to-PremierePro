import os
import time
import pygame.mixer
import yt_dlp as youtube_dl
import pymiere
import sys
import logging
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
import pystray
from PIL import Image, ImageDraw 
import re
import psutil
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

        
if platform.system() == 'Windows':
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg.exe')
elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
    # Assuming the ffmpeg binary is in the same relative path within your application
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg')
elif platform.system() == 'Linux':
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg')
else:
    # Handle other operating systems or raise an exception
    raise Exception("Unsupported operating system")


if platform.system() == 'Windows':
    appdata_path = os.environ['APPDATA']
elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
    appdata_path = os.path.expanduser('~/Library/Application Support')
elif platform.system() == 'Linux':
    appdata_path = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
else:
    # Handle other operating systems or raise an exception
    raise Exception("Unsupported operating system")

settings_path = os.path.join(appdata_path, 'YoutubetoPremiere', 'settings.json')


settings_dir = os.path.dirname(settings_path)
if not os.path.exists(settings_dir):
    os.makedirs(settings_dir)

SETTINGS_FILE = settings_path


# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('server.log'), logging.StreamHandler()])
#log_handler = logging.FileHandler('server.log')
#log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#logging.getLogger().addHandler(log_handler)

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

video_url_global = None  # Define a global variable to store the video URL
settings_global = None  # Define a global variable to store the settings

@app.after_request
def add_security_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')  # Changed line
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # Add this line
    return response


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return "Premiere is alive", 200
    elif request.method == 'POST':
        data = request.get_json()
        # ... process the data
        return jsonify(success=True), 200
    else:
        return "Method not allowed", 405


@app.route('/settings', methods=['POST'])
def update_settings():
    new_settings = request.get_json()
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(new_settings, f, indent=4)
    return jsonify(success=True), 200

@app.route('/get-video-url', methods=['GET'])
def get_video_url():
    global video_url_global
    if video_url_global is None:
        return jsonify(error="No video URL set"), 404
    return jsonify(videoUrl=video_url_global)

def is_premiere_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and 'Adobe Premiere Pro' in process.info['name']:
            return True
    return False


@app.route('/handle-video-url', methods=['POST'])
def handle_video_url():
    global video_url_global
    data = request.get_json()
    video_url_global = data.get('videoUrl')

    # Load settings and get the values
    settings = load_settings()
    if settings is None:
        logging.error("Settings not received from the extension.")
        return jsonify(error="Settings not received"), 500 

    # Extract settings values and user-provided download path
    resolution = settings.get('resolution')
    framerate = settings.get('framerate')
    user_specified_path = data.get('downloadPath')  # Corrected this line
    download_mp3 = settings.get('downloadMP3') 

    # Check if Adobe Premiere Pro is running
    if not is_premiere_running():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", "Adobe Premiere Pro is not running")
        return jsonify(error="Adobe Premiere Pro is not running"), 400

    download_path = user_specified_path if user_specified_path else settings.get('downloadPath').strip()

    # Initiate the download of the video
    download_video(video_url_global, resolution, framerate, download_path, download_mp3)
    response = jsonify(success=True)
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    return response, 200


def read_settings_from_local():
    global settings_global
    if settings_global is None:
        logging.error("Settings not received from the extension.")
        sys.exit(1)
    return settings_global


def import_video_to_premiere(video_path):
    if os.path.exists(video_path):
        logging.info(f'File already exists: {video_path}. Overwriting...')
    try:
        logging.info('Attempting to import video to Premiere...')
        proj = pymiere.objects.app.project
        logging.info('Got project object: %s', proj)
        root_bin = proj.rootItem
        logging.info('Got root bin: %s', root_bin)
        proj.importFiles([video_path], suppressUI=True, targetBin=root_bin, importAsNumberedStills=False)
        logging.info(f'Video imported to Premiere successfully: {video_path}')
    except Exception as e:
        logging.error(f'Error importing video: {e}', exc_info=True)


def sanitize_title(title):
    # Replace known problematic characters
    sanitized_title = (title.replace(":", " ")
                             .replace("：", " ")  
                             .replace("｜", " ")
                             .replace("*", " ")
                             .replace("?", " ")
                             .replace("/", " "))
    return sanitized_title

def progress_hook(d):
    if d['status'] == 'downloading':
        percentage = d['_percent_str']
        # Remove ANSI escape codes
        percentage = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', percentage)
        print(f'Progress: {percentage}')
        socketio.emit('percentage', {'percentage': percentage})

def get_default_ydl_opts():
    return {
        'quiet': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'writethumbnail': False,
        'nooverwrites': False,
    }

def convert_to_wav(m4a_path, wav_path):
    ffmpeg_command = [ffmpeg_path, '-y', '-i', m4a_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', wav_path]
    try:
        subprocess.call(ffmpeg_command)
        logging.info(f'Converted {m4a_path} to {wav_path}')
    except Exception as e:
        logging.error(f'Error converting {m4a_path} to WAV: {e}', exc_info=True)

def get_current_project_path():
    try:
        proj = pymiere.objects.app.project
        if proj and proj.path:
            project_file_path = proj.path
            project_dir_path = os.path.dirname(project_file_path)
            logging.info(f"Project directory path: {project_dir_path}")
            return project_dir_path
        else:
            logging.warning("No active project found in Premiere Pro")
            return None
    except Exception as e:
        logging.error(f'Error getting project path: {e}', exc_info=True)
        return None

    
def download_video(video_url, resolution, framerate, user_download_path, download_mp3):
    # Determine the final download path
    if user_download_path.strip():
        # Use the user-specified path if it's provided
        final_download_path = user_download_path
    else:
        # Get the directory of the current Premiere Pro project
        project_dir_path = get_current_project_path()
        if project_dir_path:
            # Create 'YoutubeToPremiere_download' directory next to the project file
            final_download_path = os.path.join(project_dir_path, 'YoutubeToPremiere_download')
            if not os.path.exists(final_download_path):
                os.makedirs(final_download_path)
        else:
            logging.error("Premiere Pro project path not found.")
            return


    with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)

    video_title = sanitize_title(info_dict['title'])
    file_extension = "wav" if download_mp3 else "mp4"

    sanitized_output_template = os.path.join(final_download_path, f"{video_title}.{file_extension}")

    ydl_opts = get_default_ydl_opts()
    ydl_opts.update({'outtmpl': sanitized_output_template, 'ffmpeg_location': ffmpeg_path})

    ydl_opts = {
        'outtmpl': sanitized_output_template,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [progress_hook],
        'writesubtitles': False,
        'writeautomaticsub': False,
        'writethumbnail': False,
        'nooverwrites': False,
    }

    if download_mp3:  # change this to something like download_audio
        ydl_opts.update({
            'format': f'bestaudio[ext=m4a]/best',
            'outtmpl': sanitized_output_template,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'nooverwrites': False,
        })
    else:
        ydl_opts.update({
            'format': f'bestvideo[ext=mp4][vcodec^=avc1][height<=1080][fps<=30]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': sanitized_output_template,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'nooverwrites': False,
        })

    sanitized_output_template = os.path.join(final_download_path, f"{video_title}.{file_extension}")
    ydl_opts['outtmpl'] = sanitized_output_template


    logging.info(f'download_mp3: {download_mp3}')  # Log the value of download_mp3
    logging.info(f'ydl_opts before download: {ydl_opts}') 
    print(ydl_opts)  # Add this line to print the ydl_opts dictionary to the console
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([video_url])
    logging.info(f'download_mp3: {download_mp3}')


    if result == 0 and download_mp3:
        sanitized_output_template = os.path.join(final_download_path, f"{video_title}.wav")
       

        # Check if the .wav file exists before trying to import it to Premiere.
        if os.path.exists(sanitized_output_template):
            # Import the WAV file into Premiere
            import_video_to_premiere(sanitized_output_template)
            socketio.emit('download-complete')  # Notify the frontend of completion if you're using a frontend
            play_notification_sound()  # Play a sound to notify the user if needed
        else:
            logging.error("Expected WAV file not found after download and conversion.")
            # Handle the error appropriately, maybe notify the user or retry the download.

    elif result == 0 and not download_mp3:
        mp4_filename = os.path.join(final_download_path, f"{video_title}.mp4")


        # Check if the .mp4 file exists before trying to import it to Premiere.
        if os.path.exists(mp4_filename):
            # Import the MP4 file into Premiere
            import_video_to_premiere(mp4_filename)
            socketio.emit('download-complete')  # Notify the frontend of completion if you're using a frontend
            play_notification_sound()  # Play a sound to notify the user if needed
        else:
            logging.error("Expected MP4 file not found after download.")
            # Handle the error appropriately, maybe notify the user or retry the download.

    else:
        logging.error("Download failed with youtube_dl.")
        # Handle the error appropriately, maybe notify the u

def play_notification_sound(volume=0.5):  # Default volume set to 50%
    pygame.mixer.init()
    pygame.mixer.music.load("notification_sound.mp3")  # Load your notification sound file
    pygame.mixer.music.set_volume(volume)  # Set the volume
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        logging.info(f'Loaded settings: {settings}')
        logging.info(f'Settings file contents: {settings}')  # Log the loaded settings
        return settings
    logging.error(f'Settings file not found: {SETTINGS_FILE}')  # Log an error if the file is not found
    return None


def main():
    logging.info('Script starting...')  # Log the starting of the script
    global settings_global
    settings_global = load_settings()  # Load settings from file
    logging.info('Settings loaded: %s', settings_global)  # Log the loaded settings
    try:
        # Start the Flask server in a separate thread
        from threading import Thread
        logging.info('Starting server thread...')  # Log before starting the server thread
        server_thread = Thread(target=lambda: socketio.run(app, host='localhost', port=3001))
        server_thread.start()
        logging.info('Server thread started')  # Log after starting the server thread
    except Exception as e:
        logging.exception(f'An error occurred: {e}')

    else:
        # Stop the server when done
        server_thread.join()

 #def create_image():
    # Check if running as a bundled application
    #if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    #    # Bundled application, icon is in the temp directory
    #    icon_path = os.path.join(sys._MEIPASS, 'icon.png')
    #else:
    #    # Not bundled, icon is in the script directory
    #    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    #print(f'Icon path: {icon_path}')  # Add this line
    #image = Image.open(icon_path)
    #return image
 ##

#def exit_action(icon, item):
   # icon.stop()
   # os._exit(0) 

#def run_tray_icon():
   # image = create_image()
  #  icon = pystray.Icon("test_icon", image, "Youtube to ¨Premiere pro", menu=pystray.Menu(pystray.MenuItem('Exit', exit_action)))
   # icon.run()

if __name__ == "__main__":
    logging.info('Script starting...')
    settings_global = load_settings()  # Load settings from file
    logging.info('Settings loaded: %s', settings_global)
    try:
        # Start the Flask server in a separate thread
        server_thread = threading.Thread(target=lambda: socketio.run(app, host='localhost', port=3001, allow_unsafe_werkzeug=True))
        server_thread.start()

        # Call run_tray_icon directly on the main thread
       # run_tray_icon()
    except Exception as e:
        logging.exception(f'An unhandled exception occurred: {e}')
    finally:
        server_thread.join()
