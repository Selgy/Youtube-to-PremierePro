import os
import subprocess
import json

def get_video_info(video_path):
    """Get video information using FFmpeg."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'stream=avg_frame_rate,r_frame_rate',
        '-of', 'json',
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def is_variable_framerate(video_info):
    """Determine if the video has a variable framerate."""
    try:
        streams = video_info['streams']
        for stream in streams:
            avg_frame_rate = eval(stream['avg_frame_rate'])
            r_frame_rate = eval(stream['r_frame_rate'])
            if avg_frame_rate != r_frame_rate:
                return True
    except (KeyError, ZeroDivisionError):
        pass
    return False

def list_footage_and_check_vfr(directory):
    """List all video files in the directory and check for variable framerate."""
    vfr_videos = []
    print("Listing all footage items and checking for variable framerate:")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp4', '.mov', '.avi', '.mkv')):  # Add more video extensions as needed
                video_path = os.path.join(root, file)
                print(f"Checking {video_path}...")
                video_info = get_video_info(video_path)
                if is_variable_framerate(video_info):
                    vfr_videos.append(video_path)

    if vfr_videos:
        print("\nVariable framerate footage found:")
        for video in vfr_videos:
            print(video)
    else:
        print("\nNo variable framerate footage found.")

# Get the directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))
list_footage_and_check_vfr(script_directory)
