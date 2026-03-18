def detect_claims(sentences: list[str]) -> list[str]:
    """
    Detect healthcare claims in sentences using keyword matching.
    Enhanced with more comprehensive keywords to catch various claim types.
    """
    # Expanded keywords indicating health claims
    keywords = {
        'treatment': ['cause', 'cure', 'treat', 'treatment', 'therapy', 'medication', 'drug'],
        'prevention': ['prevent', 'prevent', 'prevention', 'avoid', 'reduce risk'],
        'benefits': ['benefit', 'helps', 'improve', 'enhance', 'boost', 'strengthen'],
        'side_effects': ['side effect', 'adverse', 'harm', 'risk', 'danger', 'toxic'],
        'medical_conditions': ['disease', 'condition', 'illness', 'disorder', 'syndrome', 'fever', 'pain'],
        'health_general': ['health', 'healthy', 'wellness', 'nutrition', 'diet', 'supplement'],
        'body_functions': ['immune', 'digestion', 'metabolism', 'blood', 'heart', 'brain', 'weight'],
        'medical_terms': ['sugar', 'cholesterol', 'diabetes', 'cancer', 'virus', 'bacteria', 'infection'],
        'study_evidence': ['study', 'study shows', 'research', 'proven', 'evidence', 'clinical trial'],
        'quantitative': ['increase', 'reduce', 'lower', 'raise', 'more', 'less', 'percent', '%'],
    }
    
    # Flatten all keywords
    all_keywords = []
    for category, words in keywords.items():
        all_keywords.extend(words)
    
    # Remove duplicates and sort by length (longer phrases first to match them first)
    all_keywords = sorted(set(all_keywords), key=len, reverse=True)
    
    claims = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Check if any keyword appears in the sentence
        if any(keyword in sentence_lower for keyword in all_keywords):
            # Additional filter: sentence should be meaningful length
            if len(sentence.split()) >= 3:
                claims.append(sentence)
    
    return claims
