import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.corpus_index import get_model, get_corpus_embeddings, get_corpus_chunks

def retrieve_evidence(claim: str) -> list[dict]:
    model = get_model()
    corpus_emb = get_corpus_embeddings()
    chunks = get_corpus_chunks()
    
    if len(corpus_emb) == 0:
        return []
        
    claim_emb = model.encode([claim])
    similarities = cosine_similarity(claim_emb, corpus_emb)[0]
    
    # Get top 3
    top_indices = np.argsort(similarities)[-3:][::-1]
    
    evidence_list = []
    for idx in top_indices:
        confidence = float(similarities[idx])
        evidence_list.append({
            "evidence": chunks[idx]['text'],
            "source": chunks[idx]['source'], 
            "similarity_score": round(confidence, 2)
        })
    return evidence_list
