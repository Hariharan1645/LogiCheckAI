from transformers import pipeline

class FactVerifier:
    def __init__(self):
        self.nli_pipeline = pipeline(
            "text-classification",
            model="roberta-large-mnli"
        )

    def verify_claim(self, claim, evidence_list):
        results = []

        for evidence in evidence_list:
            output = self.nli_pipeline(
                f"{evidence} </s></s> {claim}"
            )[0]

            results.append({
                "evidence": evidence,
                "label": output["label"],
                "confidence": round(output["score"], 3)
            })

        return results


def aggregate_verdict(nli_results):
    labels = [r["label"] for r in nli_results]

    if "CONTRADICTION" in labels:
        return "FALSE / MISLEADING"
    elif "ENTAILMENT" in labels:
        return "TRUE"
    else:
        return "INSUFFICIENT EVIDENCE"
