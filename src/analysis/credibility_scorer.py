def calculate_credibility_score(final_results, logical_conflicts, manipulation_flags_count):
    """
    Calculate the credibility score of the creator based on the verified claims, 
    logical conflicts, and manipulative language used.
    
    final_results: list of verified claims (dicts containing 'verdict')
    logical_conflicts: list of found contradictions
    manipulation_flags_count: total number of claims/sentences flagged for manipulation
    """
    base_score = 100
    
    for result in final_results:
        verdict = result.get("verdict", "")
        if verdict in ["FALSE", "FALSE / MISLEADING"]:
            base_score -= 15
        elif verdict in ["PARTIALLY TRUE", "MISLEADING"]:
            base_score -= 5
            
    base_score -= (len(logical_conflicts) * 10)
    base_score -= (manipulation_flags_count * 5)
    
    # Bound the score between 0 and 100
    base_score = max(0, min(100, base_score))
    
    if base_score >= 80:
        rating = "High Credibility"
    elif base_score >= 50:
        rating = "Moderate Credibility"
    else:
        rating = "Low Credibility"
        
    return {
        "score": base_score,
        "rating": rating
    }
