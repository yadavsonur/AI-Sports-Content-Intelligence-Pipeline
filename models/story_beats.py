from pydantic import BaseModel


class StoryBeats(BaseModel):

    hook: str

    setup: str

    twist: str

    reveal: str

    payoff: str