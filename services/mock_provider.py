import json
from interfaces.llm_provider import LLMProvider
from models.llm_response import LLMResponse
from exceptions.provider_exceptions import ProviderExhausted


class MockProvider(LLMProvider):
    """
    Deterministic mock LLM provider for unit tests and offline end-to-end testing.
    Can be configured with custom responses or automatically produces valid mock
    JSON tailored to the prompt's requested schema.
    """

    def __init__(self, responses: dict = None, default_response: str = None, exhaust: bool = False):
        self.responses = responses or {}
        self.default_response = default_response
        self.exhaust = exhaust
        self.call_count = 0
        self.prompts_received = []

    def generate(self, prompt: str) -> LLMResponse:
        self.call_count += 1
        self.prompts_received.append(prompt)

        if self.exhaust:
            raise ProviderExhausted("Mock provider is exhausted")

        # Check explicit canned responses
        for key, resp in self.responses.items():
            if key in prompt:
                text = resp if isinstance(resp, str) else json.dumps(resp)
                return LLMResponse(text=text, provider="mock", model="mock-model")

        if self.default_response:
            return LLMResponse(text=self.default_response, provider="mock", model="mock-model")

        # Intelligent schema matching based on prompt content
        prompt_lower = prompt.lower()
        if "storydiscoveryresult" in prompt_lower or "best_story" in prompt_lower:
            data = {
                "best_story": "The Miracle of Bern: West Germany's Historic 1954 Comeback",
                "reasoning": "Underdogs West Germany overcame the legendary Hungarian Golden Team after being 2-0 down.",
                "hypotheses": [
                    {
                        "title": "The Miracle of Bern: West Germany's Historic 1954 Comeback",
                        "confidence": 0.96,
                        "evidence": [
                            "Hungary led 2-0 within 8 minutes.",
                            "West Germany rallied to win 3-2 in torrential rain.",
                            "Helmut Rahn scored the 84th-minute decider."
                        ],
                        "unresolved_questions": []
                    }
                ]
            }
        elif "editor" in prompt_lower or "selected_story" in prompt_lower or "headline" in prompt_lower:
            data = {
                "headline": "The Miracle of Bern: The 1954 Comeback That Shook Football",
                "reasoning": "High emotional stakes, historic underdog turnaround, perfect for short-form retention.",
                "confidence": 0.95
            }
        elif "narrative" in prompt_lower or "protagonist" in prompt_lower:
            data = {
                "protagonist": "Fritz Walter and Helmut Rahn of West Germany",
                "conflict": "Facing the unbeatable Hungarian Mighty Magyars who had demolished them 8-3 earlier in the tournament.",
                "turning_point": "Max Morlock's 10th-minute goal halting Hungary's momentum, followed by torrential rain favoring Adi Dassler's screw-in boots.",
                "emotional_core": "National resilience, sheer tactical grit, and refusing to surrender against world champions.",
                "lesson": "No lead is insurmountable when belief and adaptability meet the moment."
            }
        elif "story_beats" in prompt_lower or "hook" in prompt_lower and "payoff" in prompt_lower:
            data = {
                "hook": "Eight minutes in, Hungary were up 2-0. The World Cup was over. Or was it?",
                "setup": "The 1954 Final in Bern. Hungary hadn't lost a match in four years.",
                "twist": "Torrential rain turned the pitch to mud, leveling the playing field.",
                "reveal": "In the 84th minute, Helmut Rahn unleashed a thunderous left-footed strike into the bottom corner.",
                "payoff": "Final whistle blew: West Germany 3, Hungary 2. The greatest upset in World Cup history was complete."
            }
        elif "writer" in prompt_lower or "body" in prompt_lower and "ending" in prompt_lower:
            data = {
                "title": "The Miracle of Bern 1954",
                "hook": "Eight minutes into the 1954 World Cup final, the world's greatest team thought they had won.",
                "body": "Puskas and Hungary scored two quick goals, crushing German hopes. But West Germany refused to fold. Through driving rain and muddy turf, Morlock scored. Then Rahn equalized. The unstoppable Hungarians were suddenly rattled.",
                "ending": "In the 84th minute, Helmut Rahn struck the winner. The Miracle of Bern became eternal football folklore.",
                "hashtags": ["#WorldCup", "#FootballHistory", "#MiracleOfBern", "#EpicComeback"]
            }
        elif "sports_commentator" in prompt_lower or "narration" in prompt_lower:
            data = {
                "title": "The 1954 Miracle of Bern",
                "narration": "Eight minutes into the 1954 World Cup final, Hungary led 2-0. The mighty Hungarians hadn't lost in four years. But West Germany fought back through the mud and rain. Morlock made it 2-1. Rahn leveled before halftime. Then, in the 84th minute, Helmut Rahn struck into the corner! West Germany 3, Hungary 2. The miracle was complete.",
                "hashtags": ["#WorldCup", "#MiracleOfBern", "#Football", "#Comeback"]
            }
        elif "video_planner" in prompt_lower or "scenes" in prompt_lower:
            data = {
                "scenes": [
                    {
                        "start": 0.0,
                        "end": 8.0,
                        "visual_description": "West Germany vs Hungary 1954 World Cup final match",
                        "narration_segment": "Eight minutes into the 1954 World Cup final, Hungary led 2-0.",
                        "caption": "Hungary lead 2-0 in 8 minutes"
                    },
                    {
                        "start": 8.0,
                        "end": 18.0,
                        "visual_description": "Hungarian national football team Ferenc Puskas celebration",
                        "narration_segment": "The mighty Hungarians hadn't lost in four years.",
                        "caption": "Hungary unbeaten in 4 years"
                    },
                    {
                        "start": 18.0,
                        "end": 30.0,
                        "visual_description": "Football match in heavy rain mud stadium 1954",
                        "narration_segment": "But West Germany fought back through the mud and rain.",
                        "caption": "Fighting back through the mud"
                    },
                    {
                        "start": 30.0,
                        "end": 44.0,
                        "visual_description": "Helmut Rahn German footballer scoring goal",
                        "narration_segment": "Morlock made it 2-1. Rahn leveled before halftime.",
                        "caption": "West Germany level the score!"
                    },
                    {
                        "start": 44.0,
                        "end": 60.0,
                        "visual_description": "West Germany football team celebrating 1954 World Cup trophy",
                        "narration_segment": "Then, in the 84th minute, Helmut Rahn struck into the corner! West Germany 3, Hungary 2. The miracle was complete.",
                        "caption": "The Miracle of Bern is complete!"
                    }
                ]
            }
        else:
            data = {
                "result": "success",
                "message": "Mock generic response",
                "evidence": ["Evidence 1", "Evidence 2"]
            }

        return LLMResponse(
            text=json.dumps(data),
            provider="mock",
            model="mock-model"
        )
