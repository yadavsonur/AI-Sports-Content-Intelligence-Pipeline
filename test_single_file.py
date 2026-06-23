from moviepy import ImageClip


clip = (
    ImageClip(
        "assets/image3.jpg"
    )
    .with_duration(5)
)

clip.write_videofile(
    "single2.mp4",
    fps=24
)