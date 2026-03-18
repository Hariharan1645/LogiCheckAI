import re

def chunk_documents(docs: list[dict], chunk_size: int = 500) -> list[dict]:
    chunks = []
    for doc in docs:
        sentences = re.split(r'(?<=[.!?]) +', doc["text"])
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append({"text": current_chunk.strip(), "source": doc["source"]})
                current_chunk = sentence + " "
        if current_chunk:
             chunks.append({"text": current_chunk.strip(), "source": doc["source"]})
    return chunks
