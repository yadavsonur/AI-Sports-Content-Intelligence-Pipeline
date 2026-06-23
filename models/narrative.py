from pydantic import BaseModel


class Narrative(BaseModel):

    protagonist: str

    conflict: str

    turning_point: str

    emotional_core: str

    lesson: str