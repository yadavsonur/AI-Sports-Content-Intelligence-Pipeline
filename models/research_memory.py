from pydantic import BaseModel
from models.story_hypothesis import StoryHypothesis


class ResearchMemory(BaseModel):

    searches: list[str] = []

    observations: list[str] = []

    conclusions: list[str] = []

    hypotheses: list[StoryHypothesis] = []