from models.video_plan import (
    VideoPlan
)

from prompts.video_planner_prompt import (
    VIDEO_PLANNER_PROMPT
)


class VideoPlannerAgent:

    def __init__(self, llm):

        self.llm = llm

    def execute(
        self,
        final_script
    ):

        prompt = f"""
{VIDEO_PLANNER_PROMPT}

Title:

{final_script.title}

Narration:

{final_script.narration}
"""

        return self.llm.generate_structured(
            prompt,
            VideoPlan
        )