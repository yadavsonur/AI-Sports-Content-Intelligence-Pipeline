from models.chosen_story import (
    ChosenStory
)

from prompts.editor_prompt import (
    EDITOR_PROMPT
)


class EditorAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        discovery_result
    ):

        prompt = f"""
{EDITOR_PROMPT}

Stories:

{discovery_result.model_dump_json(indent=2)}
"""

        return self.llm.generate_structured(
            prompt,
            ChosenStory
        )