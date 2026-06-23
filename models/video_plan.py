from pydantic import BaseModel

from models.video_scene import (
    VideoScene
)


class VideoPlan(BaseModel):

    scenes: list[VideoScene]