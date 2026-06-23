from models.final_script import (
    FinalScript
)

from prompts.sports_commentator_prompt import (
    SPORTS_COMMENTATOR_PROMPT
)


class SportsCommentatorAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        short_script
    ):

        prompt = f"""
{SPORTS_COMMENTATOR_PROMPT}

Script:

{short_script.model_dump_json(indent=2)}
"""

        return self.llm.generate_structured(
            prompt,
            FinalScript
        )