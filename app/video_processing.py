import os
import subprocess
import logging
import yt_dlp as youtube_dl
import pymiere
import re
from flask import jsonify
import sys
import platform
import time
from app.utils import (
    is_premiere_running,
    import_video_to_premiere,
    sanitize_title,
    generate_new_filename,
    play_notification_sound,
    get_default_download_path
)

def handle_video_url(request, settings, socketio):
    data = request.get_json()
    logging.info(f"Received data: {data}")

    if not data:
        logging.error("No data received in request.")
        return jsonify(error="No data provided"), 400

    video_url = data.get('videoUrl')
    current_time = data.get('currentTime')
    download_type = data.get('downloadType')

    try:
        seconds_before = int(data.get('secondsBefore', settings['secondsBefore']))
        seconds_after = int(data.get('secondsAfter', settings['secondsAfter']))
    except (ValueError, TypeError):
        logging.error("Invalid secondsBefore or secondsAfter values.")
        return jsonify(error="Invalid time settings"), 400

    if download_type not in ['clip', 'full', 'audio']:
        logging.error(f"Invalid download type: {download_type}")
        return jsonify(error="Invalid download type"), 400

    resolution = settings.get('resolution')
    download_path = data.get('downloadPath', settings.get('downloadPath', '')).strip()
    download_mp3 = settings.get('downloadMP3')

    if not is_premiere_running():
        return jsonify(error="Adobe Premiere Pro is not running"), 400

    if download_type == 'clip':
        clip_start = max(0, current_time - seconds_before)
        clip_end = current_time + seconds_after
        download_and_process_clip(video_url, resolution, download_path, clip_start, clip_end, download_mp3, settings['ffmpeg_path'], socketio)
    elif download_type == 'full':
        download_video(video_url, resolution, download_path, download_mp3, settings['ffmpeg_path'], socketio)
    elif download_type == 'audio':
        download_audio(video_url, download_path, settings['ffmpeg_path'], socketio)

    return jsonify(success=True), 200

def verify_ffmpeg_path(ffmpeg_path):
    if not os.path.exists(ffmpeg_path):
        logging.error(f"ffmpeg binary not found at {ffmpeg_path}")
        return False
    if not os.access(ffmpeg_path, os.X_OK):
        logging.error(f"ffmpeg binary at {ffmpeg_path} is not executable")
        return False
    logging.info(f"ffmpeg binary found and executable at {ffmpeg_path}")
    return True

def download_and_process_clip(video_url, resolution, download_path, clip_start, clip_end, download_mp3, ffmpeg_path, socketio):
    clip_duration = clip_end - clip_start
    logging.info(f"Received clip parameters: clip_start={clip_start}, clip_end={clip_end}, clip_duration={clip_duration}")

    download_path = download_path if download_path else get_default_download_path()
    if download_path is None:
        logging.error("No active Premiere Pro project found.")
        return

    if not verify_ffmpeg_path(ffmpeg_path):
        socketio.emit('download-failed', {'message': 'ffmpeg not found or not executable.'})
        return

    video_info = youtube_dl.YoutubeDL().extract_info(video_url, download=False)
    sanitized_title = sanitize_title(video_info['title'])
    clip_suffix = "_clip"
    video_filename = generate_new_filename(download_path, sanitized_title, 'mp4', clip_suffix)
    video_file_path = os.path.join(download_path, video_filename)

    clip_start_str = time.strftime('%H:%M:%S', time.gmtime(clip_start))
    clip_end_str = time.strftime('%H:%M:%S', time.gmtime(clip_end))

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    # Check the operating system
    if platform.system() == "Windows":
        # For Windows, yt-dlp is inside the '_include' directory
        yt_dlp_filename = "yt-dlp.exe"
        yt_dlp_path = os.path.join(base_path, 'app', '_include', yt_dlp_filename)
    else:
        # For macOS (and potentially other Unix-like systems), yt-dlp is inside the '_internal' directory
        yt_dlp_filename = "yt-dlp"
        yt_dlp_path = os.path.join(base_path, yt_dlp_filename)

    logging.info(f"Using yt-dlp path: {yt_dlp_path}")
    logging.info(f"Using ffmpeg path: {ffmpeg_path}")

    yt_dlp_command = [
        yt_dlp_path,
        '--format', f'bestvideo[vcodec^=avc1][ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]',
        '--ffmpeg-location', ffmpeg_path,
        '--download-sections', f'*{clip_start_str}-{clip_end_str}',
        '--output', video_file_path,
        '--postprocessor-args', 'ffmpeg:-c:v copy -c:a copy',
        '--no-check-certificate',
        '--extractor-args', 'youtube:player_client=web;ios',  # Use only web and ios clients
        video_url
    ]

    logging.info(f"Running yt-dlp command: {' '.join(yt_dlp_command)}")

    try:
        subprocess.run(yt_dlp_command, check=True)
        logging.info(f"Clip downloaded: {video_file_path}")

        # Verify that the file was created and log its presence
        if os.path.exists(video_file_path):
            logging.info(f"Video file exists: {video_file_path}")
            import_video_to_premiere(video_file_path)
            logging.info("Clip imported to Premiere Pro")
            play_notification_sound()
            socketio.emit('download-complete')
        else:
            logging.error(f"Video file does not exist after download: {video_file_path}")
            socketio.emit('download-failed', {'message': 'Failed to find the downloaded clip.'})

    except subprocess.CalledProcessError as e:
        logging.error(f"Error downloading clip: {e}")
        socketio.emit('download-failed', {'message': 'Failed to download clip.'})

def download_video(video_url, resolution, download_path, download_mp3, ffmpeg_path, socketio):
    logging.info(f"Starting video download for URL: {video_url}")
    video_info = youtube_dl.YoutubeDL().extract_info(video_url, download=False)
    sanitized_title = sanitize_title(video_info['title'])
    final_download_path = download_path if download_path else get_default_download_path()
    if final_download_path is None:
        logging.error("No active Premiere Pro project found.")
        return None

    if not verify_ffmpeg_path(ffmpeg_path):
        socketio.emit('download-failed', {'message': 'ffmpeg not found or not executable.'})
        return

    extension = 'mp4' if not download_mp3 else 'wav'
    output_filename = generate_new_filename(final_download_path, sanitized_title, extension)
    sanitized_output_template = os.path.join(final_download_path, output_filename)

    ydl_opts = {
        'outtmpl': sanitized_output_template,
        'ffmpeg_location': ffmpeg_path,
        'progress_hooks': [lambda d: progress_hook(d, socketio)],
        'format': 'bestaudio[ext=m4a]/best' if download_mp3 else f'bestvideo[ext=mp4][vcodec^=avc1][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'ios']  # Use only web and ios clients, skipping android
            }
        },
    }

    logging.info(f"Using ffmpeg path: {ffmpeg_path}")
    logging.info(f"Download options: {ydl_opts}")

    def progress_hook(d, socketio):
        if d['status'] == 'downloading':
            percentage = d['_percent_str']
            percentage = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', percentage)
            logging.info(f'Progress: {percentage}')
            socketio.emit('percentage', {'percentage': percentage})

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([video_url])
        if result == 0 and os.path.exists(sanitized_output_template):
            logging.info(f"Video downloaded: {sanitized_output_template}")
            import_video_to_premiere(sanitized_output_template)
            play_notification_sound()
            socketio.emit('download-complete')
        else:
            logging.error("Video download failed.")
            socketio.emit('download-failed', {'message': 'Failed to download video.'})

def download_audio(video_url, download_path, ffmpeg_path, socketio):
    logging.info(f"Starting audio download for URL: {video_url}")
    video_info = youtube_dl.YoutubeDL().extract_info(video_url, download=False)
    sanitized_title = sanitize_title(video_info['title'])
    final_download_path = download_path if download_path else get_default_download_path()
    if final_download_path is None:
        logging.error("No active Premiere Pro project found.")
        socketio.emit('download-failed', {'message': 'No active Premiere Pro project found.'})
        return

    if not verify_ffmpeg_path(ffmpeg_path):
        socketio.emit('download-failed', {'message': 'ffmpeg not found or not executable.'})
        return

    audio_filename = generate_new_filename(final_download_path, sanitized_title, 'wav')
    sanitized_output_template = os.path.join(final_download_path, audio_filename)

    ydl_opts = {
        'outtmpl': sanitized_output_template.replace('.wav', ''),  # Avoid adding .wav twice
        'ffmpeg_location': ffmpeg_path,
        'format': 'bestaudio/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'ios']  # Use only web and ios clients, skipping android
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'progress_hooks': [lambda d: progress_hook(d, socketio)]
    }

    logging.info(f"Using ffmpeg path: {ffmpeg_path}")
    logging.info(f"Download options: {ydl_opts}")

    def progress_hook(d, socketio):
        if d['status'] == 'downloading':
            percentage = d['_percent_str']
            percentage = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', percentage)
            logging.info(f'Progress: {percentage}')
            socketio.emit('percentage', {'percentage': percentage})

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([video_url])
        if result == 0 and os.path.exists(sanitized_output_template):
            logging.info(f"Audio downloaded: {sanitized_output_template}")
            import_video_to_premiere(sanitized_output_template)
            play_notification_sound()
            socketio.emit('download-complete')
        else:
            logging.error("Audio download failed.")
            socketio.emit('download-failed', {'message': 'Failed to download audio.'})
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        socketio.emit('download-failed', {'message': 'Failed to download audio.'})

def import_video_to_premiere(video_path):
    if not os.path.exists(video_path):
        logging.error(f'File does not exist: {video_path}')
        return

    try:
        logging.info('Attempting to import video to Premiere...')
        proj = pymiere.objects.app.project
        root_bin = proj.rootItem

        proj.importFiles([video_path], suppressUI=True, targetBin=root_bin, importAsNumberedStills=False)
        logging.info(f'Video imported to Premiere successfully: {video_path}')

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(video_path)))
        transcode_folder = os.path.join(base_path, 'TRANSCODE')
        mxf_filename = os.path.splitext(os.path.basename(video_path))[0] + '.mxf'
        transcode_path = os.path.join(transcode_folder, mxf_filename)

        # Wait for the transcode file to appear
        wait_for_file(transcode_path)

        if os.path.exists(transcode_path):
            pymiere.objects.app.sourceMonitor.openFilePath(transcode_path)
            logging.info('Clip opened in source monitor.')
        else:
            logging.error(f'Transcode file not found: {transcode_path}')

    except Exception as e:
        logging.error(f'Error during import or opening clip in source monitor: {e}', exc_info=True)

def wait_for_file(path, timeout=60):
    start_time = time.time()
    while not os.path.exists(path):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"File not available after {timeout} seconds: {path}")
        time.sleep(1)
    logging.info(f"File is now available: {path}")

# Main execution
if __name__ == "__main__":
    # Add any additional setup if necessary
    logging.basicConfig(level=logging.INFO)
    logging.info("Script started")
