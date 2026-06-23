from pydantic import BaseModel


class ShortScript(BaseModel):

    title: str

    hook: str

    body: str

    ending: str

    hashtags: list[str]