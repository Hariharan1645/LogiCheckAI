import subprocess
import os

FFMPEG_PATH = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe" # works if PATH is set

def extract_audio(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    audio_path = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(video_path))[0] + ".wav"
    )

    command = [
        FFMPEG_PATH,
        "-y",
        "-i", video_path,
        "-ac", "1",
        "-ar", "16000",
        audio_path
    ]

    subprocess.run(command, check=True)
    return audio_path
