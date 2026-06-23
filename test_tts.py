from services.tts_service import (
    TTSService
)

service = TTSService()

audio = service.generate(
    text=
    """
    Curacao were losing 7-1.

    Then something happened that
    changed everything.

    They scored their first ever
    World Cup goal.
    """,

    output_path=
    "narration.mp3"
)

print(audio)