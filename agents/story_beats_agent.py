from models.story_beats import StoryBeats
from prompts.story_beats_prompt import STORY_BEATS_PROMPT


class StoryBeatsAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, chosen_story, narrative) -> StoryBeats:
        story_json = chosen_story.model_dump_json(indent=2) if hasattr(chosen_story, "model_dump_json") else str(chosen_story)
        narrative_json = narrative.model_dump_json(indent=2) if hasattr(narrative, "model_dump_json") else str(narrative)

        prompt = f"""{STORY_BEATS_PROMPT}

Chosen Story:
{story_json}

Narrative:
{narrative_json}
"""
        return self.llm.generate_structured(prompt, StoryBeats)
