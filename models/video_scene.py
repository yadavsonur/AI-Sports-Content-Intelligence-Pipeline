from typing import Union
from pydantic import BaseModel


class VideoScene(BaseModel):
    start: float
    end: float
    visual_description: str
    narration_segment: str
    caption: str
