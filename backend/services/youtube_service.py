import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(url: str) -> Optional[str]:
    # Handle multiple url formats
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:v\/|e(?:mbed)?\/|watch(?:\?|.+?)v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id: str) -> list:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        raise Exception("Transcript not available for this video")

def get_full_text(transcript: list) -> str:
    formatter = TextFormatter()
    return formatter.format_transcript(transcript)

import os
import subprocess
import uuid

import tempfile

def download_audio(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    # Use System Temp Directory instead of absolute workspace subfolder
    # to prevent local IDE / Node servers watching folder from triggering auto-restart
    audio_dir = tempfile.gettempdir()
    os.makedirs(audio_dir, exist_ok=True)
    
    # Use UID to avoid concurrent request locks or collisions overwriting target file
    request_id = str(uuid.uuid4())[:8]
    output_tmpl = os.path.join(audio_dir, f"{video_id}_{request_id}.%(ext)s")
    
    cmd = [
        "python", "-m", "yt_dlp",
        "--format", "bestaudio/best",
        "--output", output_tmpl,
        "--quiet",
        url
    ]
    
    print(f"Isolated audio download triggers... {video_id} (req: {request_id})")
    # creationflags=0x08000000 (CREATE_NO_WINDOW) prevents child crashes from sending SIGINT breaks to parent FastAPI console on Windows
    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000)
    
    if result.returncode != 0:
        raise Exception(f"Isolated Audio Download Failed: {result.stderr}")
        
    # Search for exactly what file extension yt-dlp expanded to and saved
    import glob
    downloaded_files = glob.glob(os.path.join(audio_dir, f"{video_id}_{request_id}.*"))
    
    if not downloaded_files:
        raise Exception("Audio file not found after download completion.")
        
    return downloaded_files[0]
