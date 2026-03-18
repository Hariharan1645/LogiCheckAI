import os
import whisper

# Load model globally on initialization so it doesn't reload on every request
print("Loading Whisper model (tiny) for fallbacks...")
model = whisper.load_model("tiny")

def analyze_audio(file_path: str):
    if not os.path.exists(file_path):
        return "Audio file not found."
    
    # FP16 is not supported on CPU, so we enforce fp16=False to speed up float32 paths
    # and specify language if known, usually English is fine to avoid auto-detect lag
    result = model.transcribe(file_path, fp16=False)
    return result["text"]
