from models.story_beats import (
    StoryBeats
)

from prompts.story_beats_prompt import (
    STORY_BEATS_PROMPT
)


class StoryBeatsAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        chosen_story,
        narrative
    ):

        prompt = f"""
{STORY_BEATS_PROMPT}

Narrative:

{narrative.model_dump_json(indent=2)}
"""

        return self.llm.generate_structured(
            prompt,
            StoryBeats
        )