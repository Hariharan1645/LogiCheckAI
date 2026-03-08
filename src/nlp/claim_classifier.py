from typing import Dict


MEDICAL_KEYWORDS = [
    # English
    "medicine", "drug", "tablet", "treatment", "cure",
    "disease", "health",

    # Hindi / Hinglish
    "दवा", "इलाज", "बीमारी",
    "dava", "dawa", "dhavayi", "davayi",
    "naakli", "nakli"
]


OPINION_KEYWORDS = [
    "i think", "i feel", "mujhe lagta", "mere hisab se"
]

RHETORICAL_PATTERNS = [
    "ready ho", "sach", "doctors", "nahi batayenge", "?"
]


def classify_sentence(sentence: str) -> Dict:
    """
    Classifies a sentence into claim types.

    Returns:
        Dict with sentence, label, and reason
    """

    lower = sentence.lower()

    # Rhetorical / emotional
    for pattern in RHETORICAL_PATTERNS:
        if pattern in lower:
            return {
                "label": "NON_VERIFIABLE",
                "reason": "Rhetorical or emotional phrasing detected"
            }

    # Opinion
    for word in OPINION_KEYWORDS:
        if word in lower:
            return {
                "label": "OPINION",
                "reason": "Subjective opinion phrasing detected"
            }

    # Medical factual claim
    for word in MEDICAL_KEYWORDS:
        if word in lower:
            return {
                "label": "MEDICAL_CLAIM",
                "reason": "Contains medical-related terminology"
            }

    return {
        "label": "NON_VERIFIABLE",
        "reason": "No verifiable factual content detected"
    }
