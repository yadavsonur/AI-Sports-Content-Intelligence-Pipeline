from pydantic import BaseModel


class NarrationAudio(
    BaseModel
):

    text: str

    audio_path: str

    duration: float