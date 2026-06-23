from gtts import gTTS

from models.narration_audio import (
    NarrationAudio
)


class TTSService:

    def generate(
        self,
        text,
        output_path
    ):

        tts = gTTS(
            text=text,
            lang="en"
        )

        tts.save(
            output_path
        )

        return NarrationAudio(
            text=text,
            audio_path=output_path,
            duration=0
        )