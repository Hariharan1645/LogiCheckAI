import whisper
import os
import json


def transcribe_audio(audio_path: str, output_dir: str) -> str:
    """
    Transcribes an audio file using Whisper and saves timestamped transcript.

    Args:
        audio_path (str): Path to WAV audio file
        output_dir (str): Directory to save transcript JSON

    Returns:
        str: Path to saved transcript JSON file
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    os.makedirs(output_dir, exist_ok=True)

    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Transcribing audio...")
    result = model.transcribe(audio_path)

    transcript_data = {
        "audio_file": os.path.basename(audio_path),
        "language": result.get("language"),
        "segments": []
    }

    for segment in result["segments"]:
        transcript_data["segments"].append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })

    output_path = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(audio_path))[0] + ".json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)

    print(f"Transcript saved at: {output_path}")

    return output_path
