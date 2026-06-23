from pydantic import BaseModel


class VideoScene(BaseModel):

    start: int

    end: int

    visual_description: str

    narration_segment: str

    caption: str