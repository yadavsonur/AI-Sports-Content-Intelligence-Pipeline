from pydantic import BaseModel
from typing import List


class StoryScore(BaseModel):

    headline: str

    curiosity: float

    emotional_impact: float

    retention: float

    total: float


class EditorDecision(BaseModel):

    selected_story: str

    reasoning: str

    scores: List[StoryScore]