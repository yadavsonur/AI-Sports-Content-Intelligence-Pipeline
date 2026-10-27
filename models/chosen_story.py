from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ChosenStory(BaseModel):
    headline: str
    reasoning: str
    confidence: float
    scores: List[Any] = Field(default_factory=list)
