from moviepy import (
    ImageClip,
    concatenate_videoclips
)

clips = []

for path in [
    "assets/image1.jpg",
    "assets/image2.jpg",
    "assets/image3.jpg"
]:

    clip = (
        ImageClip(path)
        .with_duration(3)
    )
    print(clip.size)

    clips.append(
        clip
    )

video = concatenate_videoclips(
    clips
)

video.write_videofile(
    "test_no_text.mp4",
    fps=24
)