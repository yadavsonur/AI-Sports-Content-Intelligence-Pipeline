from models.narrative import Narrative
from prompts.narrative_prompt import NARRATIVE_PROMPT


class NarrativeAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, chosen_story, evidence_collection) -> Narrative:
        evidence_text = "\n".join(
            [
                f"[{e.source}] {e.content} (Source: {e.url})"
                for e in evidence_collection.evidence
            ]
        )
        story_json = chosen_story.model_dump_json(indent=2) if hasattr(chosen_story, "model_dump_json") else str(chosen_story)

        prompt = f"""{NARRATIVE_PROMPT}

Chosen Story:
{story_json}

Supporting Evidence:
{evidence_text}
"""
        return self.llm.generate_structured(prompt, Narrative)
