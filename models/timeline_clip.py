from pydantic import BaseModel


class TimelineClip(BaseModel):

    asset_url: str

    duration: float

    effect: str

    caption: str