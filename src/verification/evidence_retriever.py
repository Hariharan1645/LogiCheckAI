import json
from typing import List, Dict


def retrieve_evidence(claim: str, kb_path: str = "data/medical_knowledge_base.json") -> List[Dict]:
    """
    Retrieves relevant evidence for a normalized medical claim.

    Args:
        claim (str): Normalized medical claim
        kb_path (str): Path to medical knowledge base JSON

    Returns:
        List[Dict]: List of relevant evidence entries
    """

    with open(kb_path, "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)

    claim_lower = claim.lower()
    relevant_evidence = []

    for entry in knowledge_base:
        if any(word in entry["text"].lower() for word in claim_lower.split()):
            relevant_evidence.append(entry)

    return relevant_evidence
