from pydantic import BaseModel


class Story(BaseModel):
    title: str
    summary: str
    source: str