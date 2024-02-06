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
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP
import yt_dlp as yt

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

def generate_new_filename(base_path, original_name, extension, suffix=""):
    base_filename = f"{original_name}{suffix}.{extension}"
    if not os.path.exists(os.path.join(base_path, base_filename)):
        return base_filename
    
    counter = 1
    new_name = f"{original_name}{suffix}_{counter}.{extension}"
    while os.path.exists(os.path.join(base_path, new_name)):
        counter += 1
        new_name = f"{original_name}{suffix}_{counter}.{extension}"
    return new_name

@app.route('/handle-video-url', methods=['POST'])
def handle_video_url():
    global video_url_global
    data = request.get_json()

    # Log the incoming data for debugging
    logging.info(f"Received data: {data}")

    # Error handling for missing data
    if not data:
        logging.error("No data received in request.")
        return jsonify(error="No data provided"), 400

    video_url_global = data.get('videoUrl')
    current_time = data.get('currentTime')
    download_type = data.get('downloadType')



    # Load settings here
    settings = load_settings()

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
        download_and_process_clip(video_url_global, resolution, framerate, download_path, clip_start, clip_end, current_time, download_mp3, seconds_before, seconds_after,ffmpeg_path)

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


def download_and_process_clip(video_url, resolution, framerate, user_download_path, clip_start, clip_end, current_time, download_mp3, seconds_before, seconds_after,ffmpeg_path):

    clip_duration = clip_end - clip_start
    logging.info(f"Received clip parameters: clip_start={clip_start}, clip_end={clip_end}, seconds_before={seconds_before}, seconds_after={seconds_after}, clip_duration={clip_duration}")

    download_path = user_download_path.strip() if user_download_path.strip() else get_default_download_path()
    if download_path is None:
        logging.error("No active Premiere Pro project found.")
        return



    if download_mp3:
        video_info = yt.YoutubeDL().extract_info(video_url, download=False)
        sanitized_title = sanitize_title(video_info['title'])
        clip_suffix = "_clip"
        video_filename = generate_new_filename(download_path, sanitized_title, 'mp4', clip_suffix)
        audio_filename = generate_new_filename(download_path, sanitized_title, 'wav', clip_suffix)
        video_file_path = os.path.join(download_path, video_filename)
        audio_file_path = os.path.join(download_path, audio_filename)

        ydl_opts_audio = {
            'format': 'bestaudio[ext=m4a]/best',
            'outtmpl': audio_file_path,
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [progress_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([video_url])

        temp_audio_file = f"{audio_file_path}_temp.wav"

        ffmpeg_command_audio = [
            ffmpeg_path,
            '-y',
            '-i', audio_file_path,
            '-ss', str(clip_start),
            '-t', str(clip_duration),
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            temp_audio_file
        ]

        try:
            subprocess.run(ffmpeg_command_audio, check=True)
            os.remove(audio_file_path)  # Remove the original full audio
            os.rename(temp_audio_file, audio_file_path)  # Rename the trimmed file
            logging.info(f'Trimmed audio saved to {audio_file_path}')
            import_video_to_premiere(audio_file_path)
        except subprocess.CalledProcessError as e:
            logging.error(f'Error during audio clipping process: {e}', exc_info=True)
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)  # Clean up in case of error

    else:
        video_info = yt.YoutubeDL().extract_info(video_url, download=False)
        sanitized_title = sanitize_title(video_info['title'])
        clip_suffix = "_clip"
        video_filename = generate_new_filename(download_path, sanitized_title, 'mp4', clip_suffix)
        audio_filename = generate_new_filename(download_path, sanitized_title, 'wav', clip_suffix)
        video_file_path = os.path.join(download_path, video_filename)
        audio_file_path = os.path.join(download_path, audio_filename)
        clip_start_str = time.strftime('%H:%M:%S', time.gmtime(clip_start))
        clip_end_str = time.strftime('%H:%M:%S', time.gmtime(clip_end))


        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # Check the operating system
        if platform.system() == "Windows":
            # For Windows, yt-dlp is inside the '_include' directory
            yt_dlp_filename = "yt-dlp.exe"
            yt_dlp_path = os.path.join(base_path, '_include', yt_dlp_filename)
        else:
            # For macOS (and potentially other Unix-like systems), yt-dlp is inside the '_internal' directory
            yt_dlp_filename = "yt-dlp"
            yt_dlp_path = os.path.join(base_path, yt_dlp_filename)

        # Construct the yt_dlp command line command using the dynamically determined path
        yt_dlp_command = [
            yt_dlp_path,
            '-f', f'bestvideo[vcodec^=avc1][ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]',
            '--ffmpeg-location', ffmpeg_path,  # Ensure this path is also correctly set
            '--download-sections', f'*{clip_start_str}-{clip_end_str}',
            '--output', video_file_path,
            '--postprocessor-args', 'ffmpeg:-c:v copy -c:a copy', 
            '--no-check-certificate', 
            video_url
        ]
        try:
            env = os.environ.copy()
            result = subprocess.run(yt_dlp_command, capture_output=True, text=True, env=env)
            logging.info(f"stdout: {result.stdout}")
            if result.stderr:
                logging.error(f"stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred while executing yt-dlp: {e}")

        logging.info(f"Video download completed: {video_file_path}")
        import_video_to_premiere(video_file_path)
        logging.info("Import to Premiere Pro completed")
        play_notification_sound()
        socketio.emit('download-complete')

    logging.info("Download and processing of clip completed")


def download_video(video_url, resolution, framerate, user_download_path, download_mp3):
    logging.info(f"Starting video download for URL: {video_url}")
    video_info = yt.YoutubeDL().extract_info(video_url, download=False)
    sanitized_title = sanitize_title(video_info['title'])
    # Determine the final download path
    final_download_path = user_download_path.strip() if user_download_path.strip() else get_default_download_path()
    if final_download_path is None:
        logging.error("No active Premiere Pro project found.")
        return None

    base_filename = f"{sanitized_title}.mp4"
    output_filename = generate_new_filename(final_download_path, sanitized_title, 'mp4')
    sanitized_output_template = os.path.join(final_download_path, output_filename)

    # Set youtube_dl options
    ydl_opts = {
        'outtmpl': sanitized_output_template,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [progress_hook],
        'writesubtitles': False,
        'writeautomaticsub': False,
        'writethumbnail': False,
        'nooverwrites': False,
        'format': 'bestaudio[ext=m4a]/best' if download_mp3 else f'bestvideo[ext=mp4][vcodec^=avc1][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }

    # Download the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([video_url])
        if result == 0 and os.path.exists(sanitized_output_template):
            logging.info(f"Video downloaded successfully: {sanitized_output_template}")
            import_video_to_premiere(sanitized_output_template)
            play_notification_sound()
            socketio.emit('download-complete')
        else:
            logging.error("Download failed with youtube_dl.")
            return None


def play_notification_sound(volume=0.4):  # Default volume set to 50%
    pygame.mixer.init()

    # Determine if the script is running in a bundled executable
    if getattr(sys, 'frozen', False):
        # If it's an executable, use the _MEIPASS directory
        base_path = sys._MEIPASS
    else:
        # Otherwise, use the regular script directory
        base_path = os.path.dirname(os.path.abspath(__file__))

    notification_sound_path = os.path.join(base_path, 'notification_sound.mp3')

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
    
    server_thread = threading.Thread(target=lambda: socketio.run(app, host='localhost', port=3001, allow_unsafe_werkzeug=True))
    server_thread.start()

    premiere_monitor_thread = threading.Thread(target=monitor_premiere_and_shutdown)
    premiere_monitor_thread.start()

    while not should_shutdown:
        time.sleep(1)  # Wait for the shutdown signal


    print("Shutting down the application.")
    os._exit(0)

if __name__ == "__main__":
    main()

