from models.short_script import (
    ShortScript
)

from prompts.writer_prompt import (
    WRITER_PROMPT
)


class WriterAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        chosen_story,
        narrative,
        story_beats
    ):

        prompt = f"""
{WRITER_PROMPT}

Story:
{chosen_story.model_dump_json(indent=2)}

Narrative:
{narrative.model_dump_json(indent=2)}

Story Beats:
{story_beats.model_dump_json(indent=2)}
"""

        return self.llm.generate_structured(
            prompt,
            ShortScript
        )