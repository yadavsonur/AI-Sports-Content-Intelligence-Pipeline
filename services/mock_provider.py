import json

from interfaces.llm_provider import LLMProvider
from models.llm_response import LLMResponse
from exceptions.provider_exceptions import ProviderExhausted


class MockProvider(LLMProvider):
    """
    Deterministic mock LLM provider for unit tests and offline end-to-end testing.

    Supports:
    - Custom canned responses
    - Configurable default responses
    - Provider exhaustion simulation
    - Schema-compatible responses for pipeline agents
    """

    def __init__(
        self,
        responses: dict = None,
        default_response: str = None,
        exhaust: bool = False,
    ):
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

        # 1. Explicit canned responses take precedence.
        for key, response in self.responses.items():
            if key in prompt:
                text = (
                    response
                    if isinstance(response, str)
                    else json.dumps(response)
                )
                return LLMResponse(
                    text=text,
                    provider="mock",
                    model="mock-model",
                )

        # 2. Respect an explicitly configured default response.
        if self.default_response is not None:
            return LLMResponse(
                text=self.default_response,
                provider="mock",
                model="mock-model",
            )

        prompt_lower = prompt.lower()

        # Match distinctive agent instructions rather than generic words.
        # Later prompts contain earlier outputs, so ordering matters.

        # ---------------------------------------------------------
        # VIDEO PLANNING
        # ---------------------------------------------------------
        if (
            "professional short-form video director" in prompt_lower
            or "convert a football narration into a sequence" in prompt_lower
        ):
            data = {
                "scenes": [
                    {
                        "start": 0.0,
                        "end": 6.0,
                        "visual_description": (
                            "Archival footage of the 1954 World Cup final "
                            "between West Germany and Hungary"
                        ),
                        "narration_segment": (
                            "Eight minutes into the final, Hungary led 2-0."
                        ),
                        "caption": "HUNGARY LEAD 2-0",
                    },
                    {
                        "start": 6.0,
                        "end": 12.0,
                        "visual_description": (
                            "West Germany players attacking during the "
                            "1954 World Cup final"
                        ),
                        "narration_segment": (
                            "But West Germany refused to surrender."
                        ),
                        "caption": "THE COMEBACK BEGINS",
                    },
                    {
                        "start": 12.0,
                        "end": 18.0,
                        "visual_description": (
                            "Historic football match played on a "
                            "rain-soaked pitch"
                        ),
                        "narration_segment": (
                            "Max Morlock scored, and Rahn brought them level."
                        ),
                        "caption": "WEST GERMANY FIGHT BACK",
                    },
                    {
                        "start": 18.0,
                        "end": 24.0,
                        "visual_description": (
                            "Helmut Rahn shooting toward goal in a "
                            "historic football match"
                        ),
                        "narration_segment": (
                            "Then Rahn struck again in the 84th minute."
                        ),
                        "caption": "RAHN SCORES THE WINNER",
                    },
                    {
                        "start": 24.0,
                        "end": 30.0,
                        "visual_description": (
                            "West Germany players celebrating their "
                            "1954 World Cup victory"
                        ),
                        "narration_segment": (
                            "West Germany won 3-2. The Miracle of Bern "
                            "was complete."
                        ),
                        "caption": "THE MIRACLE OF BERN",
                    },
                ]
            }

        # ---------------------------------------------------------
        # COMMENTARY / FINAL NARRATION
        # ---------------------------------------------------------
        elif (
            "elite football documentary narrator" in prompt_lower
            or "forbidden phrases" in prompt_lower
        ):
            data = {
                "title": "The Miracle of Bern: The 1954 Comeback",
                "narration": (
                    "Eight minutes into the 1954 World Cup final, "
                    "Hungary led 2-0. They were the favorites. "
                    "But West Germany refused to fold. Max Morlock "
                    "pulled one back. Helmut Rahn made it 2-2. "
                    "Then came the 84th minute. Rahn struck again. "
                    "West Germany had done it. They won 3-2, completing "
                    "the Miracle of Bern."
                ),
                "hashtags": [
                    "#WorldCup",
                    "#FootballHistory",
                    "#MiracleOfBern",
                    "#Comeback",
                ],
            }

        # ---------------------------------------------------------
        # SCRIPTWRITING
        # ---------------------------------------------------------
        elif (
            "world's best youtube shorts writers" in prompt_lower
            or "follow the story beats exactly" in prompt_lower
        ):
            data = {
                "title": "The Miracle of Bern 1954",
                "hook": (
                    "Eight minutes into the 1954 World Cup final, "
                    "Hungary were already leading 2-0."
                ),
                "body": (
                    "The Hungarian team were favorites, but West Germany "
                    "fought back. Max Morlock scored to make it 2-1. "
                    "Then Helmut Rahn equalized, bringing the final level. "
                    "The unbeaten Hungarians were suddenly under pressure."
                ),
                "ending": (
                    "In the 84th minute, Rahn scored again. West Germany "
                    "won 3-2 and stunned the football world. The Miracle "
                    "of Bern had made history."
                ),
                "hashtags": [
                    "#WorldCup",
                    "#FootballHistory",
                    "#MiracleOfBern",
                    "#Comeback",
                ],
            }

        # ---------------------------------------------------------
        # STORY BEATS
        # ---------------------------------------------------------
        elif (
            "head of audience retention" in prompt_lower
            or "maximize watch time" in prompt_lower
        ):
            data = {
                "hook": (
                    "Eight minutes in, Hungary were up 2-0. "
                    "Was the World Cup final already over?"
                ),
                "setup": (
                    "The 1954 World Cup final in Bern. Hungary arrived "
                    "as overwhelming favorites."
                ),
                "twist": (
                    "West Germany fought back after falling two goals behind."
                ),
                "reveal": (
                    "In the 84th minute, Helmut Rahn scored the decisive goal."
                ),
                "payoff": (
                    "West Germany won 3-2, completing one of football's "
                    "most famous comebacks."
                ),
            }

        # ---------------------------------------------------------
        # NARRATIVE
        # ---------------------------------------------------------
        elif (
            "world-class documentary storyteller" in prompt_lower
            or "transform football facts into a compelling story" in prompt_lower
        ):
            data = {
                "protagonist": (
                    "Fritz Walter and Helmut Rahn of West Germany"
                ),
                "conflict": (
                    "West Germany faced Hungary's legendary Mighty Magyars, "
                    "who had beaten them 8-3 earlier in the tournament."
                ),
                "turning_point": (
                    "West Germany fought back from a 2-0 deficit, "
                    "and Helmut Rahn scored the decisive goal in the "
                    "84th minute."
                ),
                "emotional_core": (
                    "Resilience, teamwork, and the refusal to surrender "
                    "against a heavily favored opponent."
                ),
                "lesson": (
                    "A difficult start does not determine the final outcome; "
                    "persistence and adaptability can change a match."
                ),
            }

        # ---------------------------------------------------------
        # EDITORIAL SELECTION
        # ---------------------------------------------------------
        elif (
            "editor-in-chief of a football media company" in prompt_lower
            or "select the single best story" in prompt_lower
        ):
            data = {
                "headline": (
                    "The Miracle of Bern: The 1954 Comeback That Shook Football"
                ),
                "reasoning": (
                    "The dramatic two-goal deficit, unexpected comeback, "
                    "and late winning goal provide a clear narrative arc "
                    "for short-form football storytelling."
                ),
                "confidence": 0.95,
                "scores": [
                    {"criterion": "Curiosity & Hook", "score": 9.5},
                    {"criterion": "Emotional Impact", "score": 9.2},
                    {"criterion": "Audience Retention", "score": 9.4},
                    {"criterion": "Shareability", "score": 9.0},
                    {"criterion": "Historical Uniqueness", "score": 9.6},
                ],
            }

        # ---------------------------------------------------------
        # STORY DISCOVERY
        # ---------------------------------------------------------
        elif (
            "research director of a football media company" in prompt_lower
            or "top story hypotheses" in prompt_lower
        ):
            data = {
                "best_story": (
                    "The Miracle of Bern: West Germany's Historic 1954 Comeback"
                ),
                "reasoning": (
                    "West Germany recovered from a two-goal deficit "
                    "to defeat the favored Hungarian team in the 1954 "
                    "World Cup final."
                ),
                "hypotheses": [
                    {
                        "title": (
                            "The Miracle of Bern: West Germany's "
                            "Historic 1954 Comeback"
                        ),
                        "confidence": 0.96,
                        "evidence": [
                            "Hungary scored twice early in the final.",
                            "West Germany came back to win the final 3-2.",
                            "Helmut Rahn scored the winning goal in the 84th minute.",
                        ],
                        "unresolved_questions": [],
                    }
                ],
            }

        # ---------------------------------------------------------
        # UNKNOWN PROMPT
        # ---------------------------------------------------------
        else:
            data = {
                "result": "success",
                "message": "Mock generic response",
                "evidence": [
                    "Evidence 1",
                    "Evidence 2",
                ],
            }

        return LLMResponse(
            text=json.dumps(data),
            provider="mock",
            model="mock-model",
        )