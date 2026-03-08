from typing import Dict


FILLER_PHRASES = [
    "aap", "tum", "bhai", "yaar", "ready ho", "sunno"
]

HINGLISH_TO_ENGLISH = {
    "naakli dhavayi": "fake medicine",
    "nakli dava": "fake medicine",
    "dava": "medicine",
    "dhavayi": "medicine",
    "ilaj": "treatment",
    "bimari": "disease"
}


def normalize_claim(sentence: str) -> Dict:
    """
    Normalizes a medical claim into a clean, declarative statement.

    Returns:
        Dict with normalized_claim and explanation
    """

    original = sentence
    text = sentence.lower()

    # Remove filler phrases
    for filler in FILLER_PHRASES:
        text = text.replace(filler, "")

    # Replace known Hinglish medical terms
    for hinglish, english in HINGLISH_TO_ENGLISH.items():
        text = text.replace(hinglish, english)

    text = text.strip()

    # Force declarative style (very basic)
    if not text.endswith("."):
        text += "."

    return {
        "original": original,
        "normalized_claim": text,
        "normalization_notes": "Rule-based normalization applied"
    }
