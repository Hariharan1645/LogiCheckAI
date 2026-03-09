class ContradictionChecker:
    def __init__(self, nli_pipeline=None):
        if nli_pipeline is not None:
            self.nli_pipeline = nli_pipeline
        else:
            from transformers import pipeline
            self.nli_pipeline = pipeline(
                "text-classification",
                model="roberta-large-mnli"
            )

    def check_contradictions(self, claims):
        """
        Evaluate pairs of claims to detect logical contradictions.
        claims: list of dicts with 'text' representing the normalized claim.
        Returns a list of logical conflicts.
        """
        conflicts = []
        n = len(claims)
        for i in range(n):
            for j in range(i + 1, n):
                claim_A = claims[i]
                claim_B = claims[j]
                
                # NLI from A to B
                # The pipeline expects f"{premise} </s></s> {hypothesis}" for roberta-large-mnli
                output = self.nli_pipeline(f"{claim_A} </s></s> {claim_B}")[0]
                
                if output["label"] == "CONTRADICTION" and output["score"] > 0.7:
                    conflicts.append({
                        "claim_1": claim_A,
                        "claim_2": claim_B,
                        "confidence": round(output["score"], 3),
                        "description": f"Internal contradiction detected between '{claim_A}' and '{claim_B}'."
                    })
        return conflicts
