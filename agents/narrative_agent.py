from models.narrative import (
    Narrative
)

from prompts.narrative_prompt import (
    NARRATIVE_PROMPT
)


class NarrativeAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        chosen_story,
        evidence_collection
    ):

        evidence_text = "\n".join(
            [
                f"[{e.source}] {e.content}"
                for e in evidence_collection.evidence
            ]
        )

        prompt = f"""
{NARRATIVE_PROMPT}

Chosen Story:

{chosen_story.model_dump_json(indent=2)}

Evidence:

{evidence_text}
"""

        return self.llm.generate_structured(
            prompt,
            Narrative
        )