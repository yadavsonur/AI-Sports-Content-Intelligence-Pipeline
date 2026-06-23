from pydantic import BaseModel


class LLMResponse(BaseModel):

    text: str

    provider: str

    model: str