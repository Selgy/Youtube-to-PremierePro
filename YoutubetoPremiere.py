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
from PIL import Image, ImageDraw 
import re
import psutil
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import shutil

should_shutdown = False



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
                    handlers=[logging.StreamHandler()])


if getattr(sys, 'frozen', False):
    # The application is frozen by PyInstaller
    script_dir = os.path.dirname(sys.executable)
else:
    # The application is running in a normal Python environment
    script_dir = os.path.dirname(os.path.abspath(__file__))

if platform.system() == 'Windows':
    # For Windows, assuming FFmpeg binary is bundled at the specified path
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg_win', 'bin', 'ffmpeg.exe')
elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
    # For macOS, assuming FFmpeg binary is bundled at the root of the application
    ffmpeg_path = os.path.join(script_dir, '_internal', 'ffmpeg', 'bin', 'ffmpeg')
    os.chmod(ffmpeg_path, 0o755)  # Ensure FFmpeg is executable
else:
    # Handle other operating systems or raise an exception
    raise Exception("Unsupported operating system")


LOCK_FILE_PATH = os.path.join(script_dir, 'app.lock')


if platform.system() == 'Windows':
    appdata_path = os.environ['APPDATA']
elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
    appdata_path = os.path.expanduser('~/Library/Application Support')
    os.chmod(appdata_path, 0o755)
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

video_url_global = None  # Global variable to store the video URL
settings_global = None  # Global variable to store the settings

@app.after_request
def add_security_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')  # Changed line
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # Add this line
    return response

def is_already_running():
    return os.path.exists(LOCK_FILE_PATH)

def create_lock_file():
    with open(LOCK_FILE_PATH, 'w') as lock_file:
        lock_file.write("")

def delete_lock_file():
    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)


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

def generate_new_filename(base_path, original_name, extension):
    base_filename = f"{original_name}.{extension}"
    if not os.path.exists(os.path.join(base_path, base_filename)):
        # If the base file does not exist, return it without a counter
        return base_filename
    
    # If the base file exists, start the counter to generate a new name
    counter = 1
    new_name = f"{original_name}_{counter}.{extension}"
    while os.path.exists(os.path.join(base_path, new_name)):
        counter += 1
        new_name = f"{original_name}_{counter}.{extension}"
    return new_name


@app.route('/handle-video-url', methods=['POST'])
def handle_video_url():
    global video_url_global
    data = request.get_json()
    settings = load_settings()
    # Log the incoming data for debugging
    logging.info(f"Received data: {data}")

    # Error handling for missing data
    if not data:
        logging.error("No data received in request.")
        return jsonify(error="No data provided"), 400

    video_url_global = data.get('videoUrl')
    current_time = data.get('currentTime')
    download_type = data.get('downloadType')

    try:
        # Retrieve secondsBefore and secondsAfter from request or settings
        seconds_before = int(data.get('secondsBefore', settings['secondsBefore']))
        seconds_after = int(data.get('secondsAfter', settings['secondsAfter']))
    except (ValueError, TypeError):
        logging.error("Invalid secondsBefore or secondsAfter values.")
        return jsonify(error="Invalid time settings"), 400


    # Error handling for invalid or missing download type
    if download_type not in ['clip', 'full']:
        logging.error(f"Invalid download type: {download_type}")
        return jsonify(error="Invalid download type"), 400

    # Load settings and get the values
    settings = load_settings()
    if settings is None:
        logging.error("Settings not received from the extension.")
        return jsonify(error="Settings not received"), 500

    resolution = settings.get('resolution')
    framerate = settings.get('framerate')
    download_path = data.get('downloadPath', settings.get('downloadPath', '')).strip()
    download_mp3 = settings.get('downloadMP3')

    # Check if Adobe Premiere Pro is running
    if not is_premiere_running():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", "Adobe Premiere Pro is not running")
        return jsonify(error="Adobe Premiere Pro is not running"), 400

    # Execute the appropriate function based on download type
    if download_type == 'clip':
        clip_start = max(0, current_time - seconds_before)
        clip_end = current_time + seconds_after
        download_and_process_clip(video_url_global, resolution, framerate, download_path, clip_start, clip_end, current_time, download_mp3, seconds_before, seconds_after)

    elif download_type == 'full':
        download_video(video_url_global, resolution, framerate, download_path, download_mp3)

    return jsonify(success=True), 200


def read_settings_from_local():
    global settings_global
    if settings_global is None:
        logging.error("Settings not received from the extension.")
        sys.exit(1)
    return settings_global

LOCK_FILE_PATH = os.path.join(script_dir, 'script.lock')

def is_already_running():
    return os.path.exists(LOCK_FILE_PATH)

def create_lock_file():
    with open(LOCK_FILE_PATH, 'w') as lock_file:
        lock_file.write("")

def delete_lock_file():
    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)


def import_video_to_premiere(video_path):
    if not os.path.exists(video_path):
        logging.error(f'File does not exist: {video_path}')
        return

    try:
        logging.info('Attempting to import video to Premiere...')
        proj = pymiere.objects.app.project
        root_bin = proj.rootItem

        # Import file
        proj.importFiles([video_path], suppressUI=True, targetBin=root_bin, importAsNumberedStills=False)
        logging.info(f'Video imported to Premiere successfully: {video_path}')

        # Open clip in source monitor
        pymiere.objects.app.sourceMonitor.openFilePath(video_path)
        logging.info('Clip opened in source monitor.')

    except Exception as e:
        logging.error(f'Error during import or opening clip in source monitor: {e}', exc_info=True)




def sanitize_title(title):
    # Allow Unicode letters, numbers, and specific special characters
    pattern = '[^\w \(\)\,\"\&\.\;\!\€\$\-\_]+'
    
    # Replace unwanted characters with a space
    sanitized_title = re.sub(pattern, ' ', title)

    # Normalize whitespace (replace multiple spaces with a single space)
    sanitized_title = re.sub(r'\s+', ' ', sanitized_title).strip()

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

def get_default_download_path():
    # Get the path of the current Premiere Pro project
    project_dir_path = get_current_project_path()
    if project_dir_path:
        default_path = os.path.join(project_dir_path, 'YoutubeToPremiere_download')
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        return default_path
    else:
        logging.error("No active Premiere Pro project found.")
        return None

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


def download_and_process_clip(video_url, resolution, framerate, user_download_path, clip_start, clip_end, current_time, download_mp3, seconds_before, seconds_after):
    clip_duration = clip_end - clip_start
    logging.info(f"Received clip parameters: clip_start={clip_start}, clip_end={clip_end}, seconds_before={seconds_before}, seconds_after={seconds_after}, clip_duration={clip_duration}")

    # Ensure that clip_duration is being calculated correctly
    logging.info(f"Clip duration calculated as: {clip_duration} seconds")

    logging.info(f"Starting download and process clip for URL: {video_url} with clip_start: {clip_start} and clip_duration: {clip_duration}")
    download_path = user_download_path.strip() if user_download_path.strip() else get_default_download_path()
    if download_path is None:
        logging.error("No active Premiere Pro project found.")
        return

    sanitized_title = sanitize_title(youtube_dl.YoutubeDL().extract_info(video_url, download=False)['title'])
    base_filename = f"{sanitized_title}_clip"
    unique_filename = generate_new_filename(download_path, base_filename, "mp4")

    clip_file_path = os.path.join(download_path, unique_filename)
  # for video
    mp3_file_path = os.path.join(download_path, unique_filename)  # base for audio

    if download_mp3:
        # Download only the audio segment as MP3
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',
            'outtmpl': f"{mp3_file_path}.%(ext)s",  # Let youtube_dl handle the extension
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'nooverwrites': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        original_mp3_file = f"{mp3_file_path}.wav"
        temp_mp3_file = f"{mp3_file_path}_temp.wav"

        ffmpeg_command = [
            ffmpeg_path,
            '-y',
            '-i', original_mp3_file,
            '-ss', str(clip_start),
            '-t', str(clip_duration),
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            temp_mp3_file
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)
            os.remove(original_mp3_file)  # Remove the original full audio
            os.rename(temp_mp3_file, original_mp3_file)  # Rename the trimmed file
            logging.info(f'Trimmed audio saved to {original_mp3_file}')
            import_video_to_premiere(original_mp3_file)
        except subprocess.CalledProcessError as e:
            logging.error(f'Error during audio clipping process: {e}', exc_info=True)
            if os.path.exists(temp_mp3_file):
                os.remove(temp_mp3_file)  # Clean up in case of error
    else:
        # Download the video clip
        ydl_opts = {
            'format': f'bestvideo[ext=mp4][vcodec^=avc1][height<={resolution}][fps<={framerate}]+bestaudio[ext=m4a]/best',
            'outtmpl': clip_file_path,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'nooverwrites': False,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Trim the video clip
        ffmpeg_command = [
            ffmpeg_path,
            '-y',
            '-i', clip_file_path,
            '-ss', str(clip_start),
            '-t', str(clip_duration),
            '-c:v', 'copy',
            '-c:a', 'copy',
            f"{clip_file_path}_temp.mp4"
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)
            os.remove(clip_file_path)  # Remove the original full video
            os.rename(f"{clip_file_path}_temp.mp4", clip_file_path)  # Rename the trimmed video file
            logging.info(f'Trimmed video saved to {clip_file_path}')
            import_video_to_premiere(clip_file_path)
        except subprocess.CalledProcessError as e:
            logging.error(f'Error during video clipping process: {e}', exc_info=True)
            if os.path.exists(f"{clip_file_path}_temp.mp4"):
                os.remove(f"{clip_file_path}_temp.mp4")  # Clean up in case of error
    play_notification_sound()
    socketio.emit('download-complete')


def download_video(video_url, resolution, framerate, user_download_path, download_mp3):
    logging.info(f"Starting video download for URL: {video_url}")

    final_download_path = user_download_path.strip() if user_download_path.strip() else get_default_download_path()
    if final_download_path is None:
        logging.error("No active Premiere Pro project found.")
        return None

    sanitized_title = sanitize_title(youtube_dl.YoutubeDL().extract_info(video_url, download=False)['title'])
    base_filename = f"{sanitized_title}"
    output_filename = generate_new_filename(final_download_path, base_filename, 'mp4')
    sanitized_output_template = os.path.join(final_download_path, output_filename)

    ydl_opts = {
        'format': f'bestvideo[height<=?{resolution}]+bestaudio/best',
        'outtmpl': sanitized_output_template,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [progress_hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    downloaded_file_path = f"{sanitized_output_template}.mkv"  # Adjust according to youtube-dl's naming
    if os.path.exists(downloaded_file_path):
        # Convert to MP4 if necessary
        ffmpeg_convert_command = [
            ffmpeg_path, '-i', downloaded_file_path, '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k', sanitized_output_template
        ]
        try:
            subprocess.run(ffmpeg_convert_command, check=True)
            os.remove(downloaded_file_path)  # Remove the original video
            logging.info(f'Video converted to MP4 and saved to {sanitized_output_template}')
        except subprocess.CalledProcessError as e:
            logging.error(f'Error during video conversion to MP4: {e}', exc_info=True)
            return None
    else:
        logging.error("Video download failed.")
        return None

    logging.info(f"Video downloaded and processed successfully: {sanitized_output_template}")
    import_video_to_premiere(sanitized_output_template)
    play_notification_sound()
    socketio.emit('download-complete')




def play_notification_sound(volume=0.4):  # Default volume set to 50%
    pygame.mixer.init()

    # Check the operating system and set the path for the notification sound
    if platform.system() == 'Darwin':  # Darwin is the system name for macOS
        notification_sound_path = os.path.join(script_dir, '_internal', 'notification_sound.mp3')
    else:
        notification_sound_path = "notification_sound.mp3"

    pygame.mixer.music.load(notification_sound_path)  # Load the notification sound file
    pygame.mixer.music.set_volume(volume)  # Set the volume
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)



def load_settings():
    # Default settings structure
    default_settings = {
        'resolution': '1080',
        'framerate': '30',
        'downloadPath': '',
        'downloadMP3': False,
        'secondsBefore': '15',
        'secondsAfter': '15'
    }

    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    else:
        settings = default_settings
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)

    logging.info(f'Loaded settings: {settings}')
    return settings


def is_premiere_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and 'Adobe Premiere Pro' in process.info['name']:
            return True
    return False

def monitor_premiere_and_shutdown():
    global should_shutdown
    while True:
        time.sleep(5)
        if not is_premiere_running():
            logging.info("Adobe Premiere Pro is not running. Initiating shutdown.")
            should_shutdown = True
            break

def run_server():
    with app.app_context():
        while not should_shutdown:
            socketio.sleep(1)  # Allows the server to check for the shutdown flag
        logging.info("Stopping the Flask-SocketIO server.")
        socketio.stop()



def main():
    logging.info(f'Starting script execution. PID: {os.getpid()}')
    global settings_global
    settings_global = load_settings()  # Load settings from file
    logging.info('Settings loaded: %s', settings_global)
    
    # Check if the application is already running
    if is_already_running():
        logging.error("Application is already running. Exiting.")
        sys.exit(1)
    else:
        create_lock_file()  # Create a lock file to indicate the app is running

    server_thread = threading.Thread(target=lambda: socketio.run(app, host='localhost', port=3001, allow_unsafe_werkzeug=True))
    server_thread.start()

    premiere_monitor_thread = threading.Thread(target=monitor_premiere_and_shutdown)
    premiere_monitor_thread.start()

    try:
        while not should_shutdown:
            time.sleep(1)  # Wait for the shutdown signal
    finally:
        delete_lock_file()  # Delete the lock file when shutting down

    print("Shutting down the application.")
    os._exit(0)

if __name__ == "__main__":
    main()


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