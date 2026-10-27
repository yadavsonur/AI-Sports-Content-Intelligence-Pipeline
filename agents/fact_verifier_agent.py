import re
from models.evidence_collection import EvidenceCollection
from models.chosen_story import ChosenStory


class FactVerifierAgent:
    """
    Verifies important factual claims in the chosen story/narrative against
    the gathered evidence collection, flagging any unsupported claims.
    """

    def __init__(self, llm=None):
        self.llm = llm

    def execute(self, chosen_story: ChosenStory, evidence_collection: EvidenceCollection) -> dict:
        headline = chosen_story.headline
        reasoning = chosen_story.reasoning
        evidence_texts = [e.content.lower() for e in evidence_collection.evidence]
        combined_evidence = " ".join(evidence_texts)

        # Extract key entities/tokens from headline
        tokens = [w for w in re.findall(r"\b[A-Za-z0-9\-]{3,}\b", headline) if w.lower() not in ("the", "and", "that", "for", "with", "from")]

        verified_claims = []
        flagged_claims = []

        # Check claim support
        matched_tokens = [t for t in tokens if t.lower() in combined_evidence]
        match_ratio = len(matched_tokens) / max(1, len(tokens))

        if match_ratio >= 0.4:
            verified_claims.append({
                "claim": f"Story subject '{headline}' is corroborated by gathered tournament research records.",
                "status": "VERIFIED",
                "matched_terms": matched_tokens
            })
        else:
            flagged_claims.append({
                "claim": f"Story headline '{headline}' contains claims with limited direct match in current evidence.",
                "status": "FLAGGED_UNSUPPORTED",
                "missing_terms": [t for t in tokens if t not in matched_tokens]
            })

        # Check numbers / scores in headline
        numbers = re.findall(r"\b\d+[\-\:]\d+\b|\b\d{4}\b", headline)
        for num in numbers:
            if num in combined_evidence:
                verified_claims.append({
                    "claim": f"Specific numerical/score milestone '{num}' verified against source records.",
                    "status": "VERIFIED"
                })
            else:
                flagged_claims.append({
                    "claim": f"Milestone '{num}' not explicitly cited in gathered evidence snippets.",
                    "status": "FLAGGED_UNSUPPORTED"
                })

        confidence = round(0.7 + (0.3 * match_ratio), 2)
        verdict = "PASS" if len(flagged_claims) <= 1 else "CAUTION"

        return {
            "verdict": verdict,
            "confidence": confidence,
            "verified_claims": verified_claims,
            "flagged_claims": flagged_claims,
            "evidence_count": len(evidence_collection.evidence),
            "sources_consulted": list(set(e.source for e in evidence_collection.evidence))
        }

