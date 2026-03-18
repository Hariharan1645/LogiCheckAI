import sys
import os

# Adjust path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.youtube_service import download_audio

def test_download():
    video_id = "0kP0SShSHeY"
    print("Testing download_audio for ID:", video_id)
    try:
        path = download_audio(video_id)
        print("Download fully finished at path:", path)
    except Exception as e:
        print("\nDownload Failed with Exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download()
