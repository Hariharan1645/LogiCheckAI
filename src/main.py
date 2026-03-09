import os
import json

from .video.audio_extractor import extract_audio
from .asr.speech_to_text import transcribe_audio
from .nlp.sentence_splitter import split_sentences
from .nlp.claim_classifier import classify_sentence
from .nlp.normalization import normalize_claim
from .verification.evidence_retriever import retrieve_evidence
from .verification.fact_verifier import FactVerifier, aggregate_verdict
from .analysis.contradiction_checker import ContradictionChecker
from .analysis.misinformation_detector import MisinformationDetector
from .analysis.credibility_scorer import calculate_credibility_score


# Global Initialization to prevent reloading heavy models for every request
print("Initializing LogiCheck AI Models. This may take a moment...")
verifier = FactVerifier()
contradiction_checker = ContradictionChecker(nli_pipeline=verifier.nli_pipeline)
misinfo_detector = MisinformationDetector()

def analyze_video(video_path: str) -> dict:
    """
    Main orchestration function for LogiCheck AI.
    Runs the full end-to-end pipeline on a given video file.
    Returns the final analytical JSON dictionary.
    """
    
    # -----------------------------
    # Paths (relative to root)
    # -----------------------------
    audio_output_dir = "data/extracted_audio"
    transcript_output_dir = "data/transcripts"
    output_dir = "data/output"

    os.makedirs(audio_output_dir, exist_ok=True)
    os.makedirs(transcript_output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------
    # Step 1: Extract audio
    # -----------------------------
    print(f"Extracting Audio from {video_path}")
    audio_path = extract_audio(video_path, audio_output_dir)

    # -----------------------------
    # Step 2: Speech-to-text (ASR)
    # -----------------------------
    print(f"Transcribing Audio: {audio_path}")
    transcript_path = transcribe_audio(audio_path, transcript_output_dir)

    # -----------------------------
    # Step 3: Sentence splitting
    # -----------------------------
    sentences = split_sentences(transcript_path)

    # -----------------------------
    # Step 4: Evaluate Pipeline
    # -----------------------------
    final_results = []
    all_manipulation_flags = 0

    print("\nStarting Medical Claim Verification Pipeline...\n")

    # -----------------------------
    # Step 5: Process each sentence
    # -----------------------------
    for s in sentences:
        sentence_text = s["sentence"]
        timestamp = {
            "start": s.get("start"),
            "end": s.get("end")
        }

        # Analyze manipulation
        manipulation_analysis = misinfo_detector.detect_manipulation(sentence_text)
        if manipulation_analysis["is_flagged"]:
            all_manipulation_flags += 1

        classification = classify_sentence(sentence_text)

        if classification["label"] != "MEDICAL_CLAIM":
            continue

        # Normalize claim
        normalized = normalize_claim(sentence_text)

        # Retrieve evidence
        evidence = retrieve_evidence(normalized["normalized_claim"])
        evidence_texts = [e["text"] for e in evidence]

        print(f"Claim: {normalized['normalized_claim']}")
        print(f"Evidence Found: {len(evidence)}")

        # Verify claim using NLI
        if evidence_texts:
            nli_results = verifier.verify_claim(
                normalized["normalized_claim"],
                evidence_texts
            )
            verdict = aggregate_verdict(nli_results)
        else:
            nli_results = []
            verdict = "INSUFFICIENT_EVIDENCE"

        print(f"Verdict: {verdict}")

        # Log details
        for r in nli_results:
            print(f"- {r['label']} ({r['confidence']})")
            print(f"  Evidence: {r['evidence']}")

        print("-" * 60)

        # Explanations
        simplified_explanation = f"Based on the evidence retrieved, this medical claim is considered {verdict}."
        detailed_explanation = f"The claim '{normalized['normalized_claim']}' was checked against medical knowledge base. {len(evidence_texts)} sources were evaluated using Natural Language Inference models, resulting in an aggregate algorithmic verdict of {verdict}."

        # Store result
        final_results.append({
            "original_sentence": sentence_text,
            "normalized_claim": normalized["normalized_claim"],
            "timestamp": timestamp,
            "verdict": verdict,
            "manipulation_analysis": manipulation_analysis,
            "explanations": {
                "simplified": simplified_explanation,
                "detailed": detailed_explanation
            },
            "evidence": evidence,
            "nli_results": nli_results
        })

    # -----------------------------
    # Step 6: Contradiction Check & Credibility
    # -----------------------------
    normalized_claims = [r["normalized_claim"] for r in final_results]
    logical_conflicts = contradiction_checker.check_contradictions(normalized_claims)
    
    credibility = calculate_credibility_score(final_results, logical_conflicts, all_manipulation_flags)

    # Calculate overall verdict
    verdicts = [r["verdict"] for r in final_results]
    if "FALSE / MISLEADING" in verdicts or "FALSE" in verdicts:
        overall_video_verdict = "FALSE / MISLEADING"
    elif "PARTIALLY TRUE" in verdicts or "MISLEADING" in verdicts:
        overall_video_verdict = "MISLEADING"
    elif "TRUE" in verdicts:
        overall_video_verdict = "VERIFIED"
    else:
        overall_video_verdict = "UNVERIFIED"

    final_output = {
        "video_analysis": {
            "overall_verdict": overall_video_verdict,
            "creator_credibility": credibility,
            "logical_conflicts": logical_conflicts,
            "total_claims_analyzed": len(final_results),
            "manipulative_sentences_detected": all_manipulation_flags
        },
        "claims_breakdown": final_results,
        "disclaimer": "This tool is for educational and informational purposes only and does not replace professional medical advice."
    }

    # -----------------------------
    # Step 7: Save and Return Output
    # -----------------------------
    output_path = os.path.join(output_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Pipeline Complete! Output length: {len(final_output)}")
    
    return final_output


if __name__ == "__main__":
    analyze_video("data/input_videos/test_video.mp4")
