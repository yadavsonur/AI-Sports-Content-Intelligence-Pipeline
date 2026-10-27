from models.short_script import ShortScript
from prompts.writer_prompt import WRITER_PROMPT


class WriterAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, chosen_story, narrative, story_beats) -> ShortScript:
        story_json = chosen_story.model_dump_json(indent=2) if hasattr(chosen_story, "model_dump_json") else str(chosen_story)
        narrative_json = narrative.model_dump_json(indent=2) if hasattr(narrative, "model_dump_json") else str(narrative)
        beats_json = story_beats.model_dump_json(indent=2) if hasattr(story_beats, "model_dump_json") else str(story_beats)

        prompt = f"""{WRITER_PROMPT}

Story:
{story_json}

Narrative:
{narrative_json}

Story Beats:
{beats_json}
"""
        return self.llm.generate_structured(prompt, ShortScript)
