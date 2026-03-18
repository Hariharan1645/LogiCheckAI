import traceback
import sys
import os
from dotenv import load_dotenv

# Adjust python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()


from services.youtube_service import extract_video_id, get_transcript, get_full_text
from services.text_normalizer import clean_and_normalize
from services.text_processing import split_into_sentences
from services.claim_detection import detect_claims
from services.claim_rewriter import rewrite_claim
from services.corpus_loader import load_documents
from services.corpus_chunker import chunk_documents
from services.corpus_index import init_index
from services.semantic_verification import retrieve_evidence
from services.verdict_engine import classify_verdict
from services.reasoning_service import generate_video_reasoning

def run_test():
    url = "https://www.youtube.com/watch?v=0kP0SShSHeY"
    try:
        print("Loading corpus...")
        corpus_dir = os.path.join(os.path.dirname(__file__), "corpus")
        docs = load_documents(corpus_dir)
        chunks = chunk_documents(docs)
        init_index(chunks)
        print("Corpus loaded and indexed.")

        print("Extracting video ID for:", url)
        video_id = extract_video_id(url)
        print("Video ID:", video_id)

        print("Fetching transcript...")
        transcript = get_transcript(video_id)
        full_text = get_full_text(transcript)
        print("Transcript downloaded. Length:", len(full_text))

        print("Processing text...")
        normalized = clean_and_normalize(full_text)
        sentences = split_into_sentences(normalized)
        claims = detect_claims(sentences)
        print(f"Claims detected: {len(claims)}")

        results = []
        for claim in claims:
            rewritten = rewrite_claim(claim)
            evidence = retrieve_evidence(rewritten)
            verdict = classify_verdict(evidence)
            results.append({
                "original_claim": claim,
                "rewritten_claim": rewritten,
                "evidence": evidence,
                "verdict": verdict
            })

        print("Generating reasoning...")
        reasoning = generate_video_reasoning(full_text, results)
        print("\n=== REASONING ===\n")
        print(reasoning)
        
    except Exception as e:
        print("\nPipeline failed with exception:")
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
