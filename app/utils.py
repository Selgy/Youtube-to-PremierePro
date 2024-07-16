import os
import json
import psutil
import sys
import platform
import logging
import string
import pygame
import pymiere
import time
import shutil

def load_settings():
    default_settings = {
        'resolution': '1080',
        'downloadPath': '',
        'downloadMP3': False,
        'secondsBefore': '15',
        'secondsAfter': '15'
    }

    script_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

    if platform.system() == 'Windows':
        appdata_path = os.environ['APPDATA']
        ffmpeg_path = os.path.join(script_dir, 'ffmpeg_win', 'bin', 'ffmpeg.exe')
    elif platform.system() == 'Darwin':
        appdata_path = os.path.expanduser('~/Library/Application Support')
        ffmpeg_path = os.path.join(script_dir, '_internal', 'ffmpeg', 'bin', 'ffmpeg')
        if os.path.exists(ffmpeg_path):
            os.chmod(ffmpeg_path, 0o755)
        else:
            logging.error(f"ffmpeg not found at {ffmpeg_path}. Please ensure ffmpeg is installed.")
            raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")
    elif platform.system() == 'Linux':
        appdata_path = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        ffmpeg_path = 'ffmpeg'  # Assuming ffmpeg is in the PATH
        # Verify that ffmpeg exists in PATH
        if not shutil.which(ffmpeg_path):
            logging.error("ffmpeg not found in PATH. Please install ffmpeg.")
            raise FileNotFoundError("ffmpeg not found in PATH")
    else:
        raise Exception("Unsupported operating system")

    settings_path = os.path.join(appdata_path, 'YoutubetoPremiere', 'settings.json')
    if not os.path.exists(os.path.dirname(settings_path)):
        os.makedirs(os.path.dirname(settings_path))

    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    else:
        settings = default_settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

    settings['SETTINGS_FILE'] = settings_path
    settings['ffmpeg_path'] = ffmpeg_path

    logging.info(f'Loaded settings: {settings}')
    return settings


def monitor_premiere_and_shutdown():
    global should_shutdown

    # Find the process ID of Premiere Pro
    premiere_pro_process = None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and 'Adobe Premiere Pro' in process.info['name']:
            premiere_pro_process = process
            break

    if premiere_pro_process:
        # Wait for the Premiere Pro process to terminate
        premiere_pro_process.wait()
        logging.info("Adobe Premiere Pro has been closed. Initiating shutdown.")
        should_shutdown = True
    else:
        logging.info("Adobe Premiere Pro is not running.")

def get_default_download_path():
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

        # Skip waiting for the transcode file and open the original video file in source monitor
        pymiere.objects.app.sourceMonitor.openFilePath(video_path)
        logging.info('Clip opened in source monitor.')

    except Exception as e:
        logging.error(f'Error during import or opening clip in source monitor: {e}', exc_info=True)


def sanitize_title(title):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_title = ''.join(c for c in title if c in valid_chars)
    sanitized_title = sanitized_title.strip()
    return sanitized_title

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

def play_notification_sound(volume=0.4):  # Default volume set to 50%
    pygame.mixer.init()

    base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    notification_sound_path = os.path.join(base_path, 'notification_sound.mp3')

    pygame.mixer.music.load(notification_sound_path)  # Load the notification sound file
    pygame.mixer.music.set_volume(volume)  # Set the volume
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def is_premiere_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and 'Adobe Premiere Pro' in process.info['name']:
            return True
    return False
