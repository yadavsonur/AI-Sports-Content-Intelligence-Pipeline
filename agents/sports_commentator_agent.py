from models.final_script import FinalScript
from prompts.sports_commentator_prompt import SPORTS_COMMENTATOR_PROMPT


class SportsCommentatorAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, short_script) -> FinalScript:
        if hasattr(short_script, "model_dump_json"):
            script_json = short_script.model_dump_json(indent=2)
        elif isinstance(short_script, str):
            script_json = short_script
        else:
            import json
            try:
                script_json = json.dumps(short_script, indent=2)
            except Exception:
                script_json = str(short_script)

        prompt = f"""{SPORTS_COMMENTATOR_PROMPT}

Script:
{script_json}
"""
        return self.llm.generate_structured(prompt, FinalScript)
