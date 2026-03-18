import re

def clean_and_normalize(text: str) -> str:
    # Remove excessive newlines and whitespace
    text = re.sub(r'\s+', ' ', text)
    # Basic cleaning
    return text.strip()
