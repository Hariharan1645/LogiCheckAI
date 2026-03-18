from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
from services.whisper_service import analyze_audio
from services.reasoning_service import generate_video_reasoning
import os
import traceback
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing backend... Loading models and corpus.")
    corpus_dir = os.path.join(os.path.dirname(__file__), "corpus")
    docs = load_documents(corpus_dir)
    chunks = chunk_documents(docs)
    init_index(chunks)
    print("Backend initialization complete.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log detailed crash traceback to a file for debugging
    log_file = os.path.join(os.path.dirname(__file__), "crash_log.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Exception Type: {type(exc).__name__}\n")
        f.write(f"Exception Message: {str(exc)}\n\n")
        f.write("Full Traceback:\n")
        traceback.print_exc(file=f)
    return JSONResponse(
        status_code=500, 
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

@app.get("/")
def read_root():
    return {"message": "Backend is running successfully"}

@app.get("/analyze")
def analyze_local_audio():
    audio_path = os.path.join(os.path.dirname(__file__), "audio", "sample.wav")
    try:
        text = analyze_audio(audio_path)
        
        # apply same pipeline as youtube
        normalized_text = clean_and_normalize(text)
        sentences = split_into_sentences(normalized_text)
        claims = detect_claims(sentences)
        
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
            
        reasoning = generate_video_reasoning(text, results)
        return {"claims": results, "reasoning": reasoning}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze_youtube")
def analyze_youtube(url: str):
    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    # Speed Cache to avoid CPU loads on duplicates
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{video_id}.json")
    
    import json
    if os.path.exists(cache_path):
        print(f"Loading cached analysis for {video_id}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        transcript_raw = get_transcript(video_id)
        full_text = get_full_text(transcript_raw)
    except Exception as e:
        print(f"Transcript failed: {e}. Falling back to Whisper AI...")
        try:
            from services.youtube_service import download_audio
            from services.whisper_service import analyze_audio
            
            # Download audio
            audio_path = download_audio(video_id)
            # Transcribe
            full_text = analyze_audio(audio_path)
            
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Analysis failed. Transcript error: {e}. Whisper fallback error: {fallback_error}")
    normalized_text = clean_and_normalize(full_text)
    sentences = split_into_sentences(normalized_text)
    claims = detect_claims(sentences)
    
    results = []
    for claim in claims:
        # Avoid too short items
        if len(claim.split()) < 3:
            continue
            
        rewritten = rewrite_claim(claim)
        evidence = retrieve_evidence(rewritten)
        verdict = classify_verdict(evidence)
        
        results.append({
            "original_claim": claim,
            "rewritten_claim": rewritten,
            "evidence": evidence,
            "verdict": verdict
        })
        
    reasoning = generate_video_reasoning(full_text, results)
    
    # Store cache response
    response_payload = {"claims": results, "reasoning": reasoning}
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(response_payload, f, indent=4)
        
    return response_payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
