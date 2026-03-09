import requests
from typing import List, Dict

# Basic stop words to filter out for better search queries
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", 
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", 
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", 
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", 
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", 
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", 
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
}

def extract_keywords(claim: str) -> str:
    """Removes common stop words to create a dense search query."""
    words = claim.lower().replace(".", "").replace(",", "").replace('"', '').split()
    keywords = [word for word in words if word not in STOP_WORDS]
    # Rejoin the top 4 most critical keywords to avoid overly broad queries
    return " ".join(keywords[:4])


def retrieve_evidence(claim: str, kb_path: str = None) -> List[Dict]:
    """
    Queries the live Europe PubMed Central (Europe PMC) REST API to 
    fetch real medical literature as evidence for the normalized claim.
    """
    
    query = extract_keywords(claim)
    if not query:
        return []

    print(f"  [Europe PMC API] Searching literature for: '{query}'")

    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f'"{query}" OR {query}',  # Try exact phrase first, then loose match
        "format": "json",
        "resultType": "core",  # Brings back full abstracts
        "pageSize": 3          # Only get the top 3 most relevant papers
    }

    relevant_evidence = []
    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("resultList", {}).get("result", [])
        
        for paper in results:
            # We must only return papers that actually have an abstract to verify against
            abstract = paper.get("abstractText")
            title = paper.get("title")
            
            if abstract and title:
                # Strip basic HTML tags often found in PMC abstracts
                clean_abstract = abstract.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
                
                # Format to match the previous local KB standard
                relevant_evidence.append({
                    "id": paper.get("id", "PMC_UNKNOWN"),
                    "text": clean_abstract,
                    "source": f"Europe PMC: {title}",
                    "url": f"https://europepmc.org/article/MED/{paper.get('pmid', '')}",
                    "reliability": 0.95  # Assumed high reliability for peer-reviewed literature
                })

    except requests.exceptions.RequestException as e:
        print(f"  [Error] Failed to reach Europe PMC: {str(e)}")
        
    except json.JSONDecodeError:
        print(f"  [Error] API returned invalid JSON.")

    return relevant_evidence
