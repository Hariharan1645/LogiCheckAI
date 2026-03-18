from sentence_transformers import SentenceTransformer
import numpy as np

model = None
corpus_embeddings = None
corpus_chunks = []

def init_index(chunks: list[dict]):
    global model, corpus_embeddings, corpus_chunks
    if model is None:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    corpus_chunks = chunks
    if chunks:
        texts = [c['text'] for c in chunks]
        corpus_embeddings = model.encode(texts)
    else:
        corpus_embeddings = []

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return model
    
def get_corpus_embeddings():
    return corpus_embeddings

def get_corpus_chunks():
    return corpus_chunks
