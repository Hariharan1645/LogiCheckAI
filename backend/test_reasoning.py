import sys
import os

# Adjust path
# Just append backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.reasoning_service import generate_video_reasoning

def test_reasoning():
    claims = [
        {
            "original_claim": "Drinking water cures diabetes",
            "verdict": {"verdict": "No Evidence", "confidence": 0.1}
        }
    ]

    text = "This is a transcript of a guy talking about drinking water and how it claims to cure diseases."

    print("Testing reasoning with Groq...")
    result = generate_video_reasoning(text, claims)
    print("\n=== RESULT ===\n")
    print(result)

if __name__ == "__main__":
    test_reasoning()
