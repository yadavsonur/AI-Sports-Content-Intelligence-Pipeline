from pydantic import BaseModel


class StoryCandidate(BaseModel):

    title: str

    summary: str

    source: str

    confidence: float