from pydantic import BaseModel


class ChosenStory(BaseModel):

    headline: str

    reasoning: str

    confidence: float