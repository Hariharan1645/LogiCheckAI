import os

def load_documents(corpus_dir: str) -> list[dict]:
    docs = []
    if not os.path.exists(corpus_dir):
        return docs
    
    for filename in os.listdir(corpus_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(corpus_dir, filename), 'r', encoding='utf-8') as f:
                docs.append({
                    "text": f.read(),
                    "source": filename
                })
    return docs
