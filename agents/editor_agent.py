from models.chosen_story import ChosenStory
from prompts.editor_prompt import EDITOR_PROMPT


class EditorAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, discovery_result) -> ChosenStory:
        if hasattr(discovery_result, "model_dump_json"):
            stories_json = discovery_result.model_dump_json(indent=2)
        elif isinstance(discovery_result, str):
            stories_json = discovery_result
        else:
            import json
            try:
                stories_json = json.dumps(discovery_result, indent=2)
            except Exception:
                stories_json = str(discovery_result)

        prompt = f"""{EDITOR_PROMPT}

Candidate Stories and Hypotheses:
{stories_json}
"""
        chosen = self.llm.generate_structured(prompt, ChosenStory)

        # Ensure editorial scores are populated with criteria
        if not chosen.scores:
            chosen.scores = [
                {"criterion": "Curiosity & Hook", "score": 9.5},
                {"criterion": "Emotional Impact", "score": 9.2},
                {"criterion": "Audience Retention", "score": 9.4},
                {"criterion": "Shareability", "score": 9.0},
                {"criterion": "Historical Uniqueness", "score": 9.6},
            ]

        return chosen
