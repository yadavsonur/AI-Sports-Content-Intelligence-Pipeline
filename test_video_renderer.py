from services.video_renderer import (
    VideoRenderer
)

from models.timeline_clip import (
    TimelineClip
)

from models.video_timeline import (
    VideoTimeline
)

from PIL import Image


print(
    "\n========== IMAGE INFO ==========\n"
)

for path in [
    "assets/image1.jpg",
    "assets/image2.jpg",
    "assets/image3.jpg"
]:

    img = Image.open(path)

    print(
        f"{path} -> "
        f"{img.size}"
    )

print(
    "\n========== BUILDING TIMELINE ==========\n"
)

timeline = VideoTimeline(
    clips=[

        TimelineClip(
            asset_url=
            "assets/image1.jpg",

            duration=3,

            effect=
            "none",

            caption=
            "SCENE 1"
        ),

        TimelineClip(
            asset_url=
            "assets/image2.jpg",

            duration=3,

            effect=
            "none",

            caption=
            "SCENE 2"
        ),

        TimelineClip(
            asset_url=
            "assets/image3.jpg",

            duration=3,

            effect=
            "none",

            caption=
            "SCENE 3"
        )
    ]
)

for index, clip in enumerate(
    timeline.clips
):

    print(
        f"\nClip {index}"
    )

    print(
        f"Asset: {clip.asset_url}"
    )

    print(
        f"Duration: {clip.duration}"
    )

    print(
        f"Caption: {clip.caption}"
    )

print(
    "\n========== START RENDER ==========\n"
)

renderer = VideoRenderer()

output = renderer.render(
    timeline,
    "output.mp4"
)

print(
    "\n========== FINISHED ==========\n"
)

print(
    f"Output: {output}"
)