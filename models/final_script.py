from pydantic import BaseModel


class FinalScript(BaseModel):

    title: str

    narration: str

    hashtags: list[str]