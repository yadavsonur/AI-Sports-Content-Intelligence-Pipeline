from pydantic import BaseModel

from models.story_hypothesis import (
    StoryHypothesis
)


class StoryDiscoveryResult(BaseModel):

    best_story: str

    reasoning: str

    hypotheses: list[StoryHypothesis]