from pydantic import BaseModel


class StoryHypothesis(BaseModel):

    title: str

    confidence: float

    evidence: list[str]

    unresolved_questions: list[str]