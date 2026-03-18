import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.youtube_service import get_transcript, download_audio, get_full_text
from services.whisper_service import analyze_audio
from services.text_normalizer import clean_and_normalize
from services.text_processing import split_into_sentences
from services.claim_detection import detect_claims
from services.claim_rewriter import rewrite_claim
from services.semantic_verification import retrieve_evidence
from services.verdict_engine import classify_verdict
from services.reasoning_service import generate_video_reasoning

from services.corpus_loader import load_documents
from services.corpus_chunker import chunk_documents
from services.corpus_index import init_index

def test_on_url():
    video_id = "1p-D_wb3CMo"
    print(f"Testing Analysis Pipeline for ID: {video_id}")
    
    print("Initialising Corpus index standard...")
    corpus_dir = os.path.join(os.path.dirname(__file__), "corpus")
    docs = load_documents(corpus_dir)
    chunks = chunk_documents(docs)
    init_index(chunks)
    print("Index ready.")
    
    full_text = ""
    try:
        print("1. Fetching Transcript...")
        transcript_raw = get_transcript(video_id)
        full_text = get_full_text(transcript_raw)
        print("Transcript success.")
    except Exception as e:
        print(f"Transcript failed: {e}. Falling back to Whisper AI...")
        try:
            print("2. Downloading Audio (Fallback)...")
            audio_path = download_audio(video_id)
            print(f"Audio downloaded to: {audio_path}")
            
            print("3. Transcribing with Whisper...")
            full_text = analyze_audio(audio_path)
            print("Whisper success.")
        except Exception as fallback_error:
             print(f"Fallback Failed: {fallback_error}")
             return

    print(f"Full Text length: {len(full_text)}")
    print("4. Standard pipeline processing...")
    normalized_text = clean_and_normalize(full_text)
    sentences = split_into_sentences(normalized_text)
    claims = detect_claims(sentences)
    
    print(f"Claims found: {len(claims)}")
    
    results = []
    for claim in claims:
        rewritten = rewrite_claim(claim)
        evidence = retrieve_evidence(rewritten)
        verdict = classify_verdict(evidence)
        results.append({
            "original_claim": claim,
            "verdict": verdict
        })

    print("5. Generating reasoning with Groq...")
    reasoning = generate_video_reasoning(full_text, results)
    print("\n=== REASONING ===\n")
    print(reasoning)
    
    # Save output to read fully
    with open("standalone_results.txt", "w", encoding="utf-8") as f:
        f.write(reasoning)

if __name__ == "__main__":
    test_on_url()
