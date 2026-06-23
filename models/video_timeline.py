from pydantic import BaseModel

from models.timeline_clip import (
    TimelineClip
)


class VideoTimeline(BaseModel):

    clips: list[TimelineClip]