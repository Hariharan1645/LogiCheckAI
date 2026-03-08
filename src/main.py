import os
import json

from video.audio_extractor import extract_audio
from asr.speech_to_text import transcribe_audio
from nlp.sentence_splitter import split_sentences
from nlp.claim_classifier import classify_sentence
from nlp.normalization import normalize_claim
from verification.evidence_retriever import retrieve_evidence
from verification.fact_verifier import FactVerifier, aggregate_verdict


def main():
    # -----------------------------
    # Paths
    # -----------------------------
    video_path = "data/input_videos/test_video.mp4"
    audio_output_dir = "data/extracted_audio"
    transcript_output_dir = "data/transcripts"
    output_dir = "data/output"

    os.makedirs(audio_output_dir, exist_ok=True)
    os.makedirs(transcript_output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------
    # Step 1: Extract audio
    # -----------------------------
    audio_path = extract_audio(video_path, audio_output_dir)

    # -----------------------------
    # Step 2: Speech-to-text (ASR)
    # -----------------------------
    transcript_path = transcribe_audio(audio_path, transcript_output_dir)

    # -----------------------------
    # Step 3: Sentence splitting
    # -----------------------------
    sentences = split_sentences(transcript_path)

    # -----------------------------
    # Step 4: Initialize verifier
    # -----------------------------
    verifier = FactVerifier()
    final_results = []

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

        # Store result
        final_results.append({
            "original_sentence": sentence_text,
            "normalized_claim": normalized["normalized_claim"],
            "timestamp": timestamp,
            "verdict": verdict,
            "evidence": evidence,
            "nli_results": nli_results
        })

    # -----------------------------
    # Step 6: Save final output
    # -----------------------------
    output_path = os.path.join(output_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Final results saved to {output_path}")


if __name__ == "__main__":
    main()
