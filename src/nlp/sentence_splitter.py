import json
import re
from typing import List, Dict


def split_sentences(transcript_path: str) -> List[Dict]:
    """
    Splits transcript segments into individual sentences.

    Args:
        transcript_path (str): Path to transcript JSON file

    Returns:
        List[Dict]: List of sentence objects with text and timestamps
    """

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    sentences = []

    sentence_delimiters = r"[\.!?।]"

    for segment in transcript["segments"]:
        text = segment["text"]

        # Split based on punctuation
        parts = re.split(sentence_delimiters, text)

        for part in parts:
            cleaned = part.strip()

            if cleaned:
                sentences.append({
                    "sentence": cleaned,
                    "start": segment["start"],
                    "end": segment["end"]
                })

    return sentences
