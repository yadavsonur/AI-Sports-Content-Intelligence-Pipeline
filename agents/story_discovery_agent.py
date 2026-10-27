from models.story_discovery_result import StoryDiscoveryResult
from prompts.story_discovery_prompt import STORY_DISCOVERY_PROMPT


class StoryDiscoveryAgent:

    def __init__(self, reliable_llm):
        self.llm = reliable_llm

    def execute(self, evidence_collection) -> StoryDiscoveryResult:
        evidence_text = "\n".join(
            [
                f"[{e.source}] {e.content} (Source URL: {e.url})"
                for e in evidence_collection.evidence
            ]
        )

        prompt = f"""{STORY_DISCOVERY_PROMPT}

Gathered Evidence:
{evidence_text}
"""
        return self.llm.generate_structured(prompt, StoryDiscoveryResult)
