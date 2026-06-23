from moviepy import TextClip

clip = TextClip(
    text="HELLO WORLD",
    font_size=100,
    color="white"
)

print(
    "TextClip size:",
    clip.size
)