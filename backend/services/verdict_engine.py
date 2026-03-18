def classify_verdict(evidence_list: list) -> dict:
    if not evidence_list:
        return {"verdict": "No Evidence", "confidence": 0.0}
        
    top_score = evidence_list[0]['similarity_score']
    
    if top_score >= 0.75:
        verdict = "Strongly Supported"
    elif top_score >= 0.60:
        verdict = "Supported"
    elif top_score >= 0.50:
        verdict = "Weakly Supported"
    elif top_score >= 0.40:
        verdict = "Insufficient Evidence"
    else:
        verdict = "No Evidence"
        
    return {
        "verdict": verdict,
        "confidence": top_score
    }
