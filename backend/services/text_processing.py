import re

def split_into_sentences(text: str) -> list[str]:
    # A simple regex for splitting sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]
