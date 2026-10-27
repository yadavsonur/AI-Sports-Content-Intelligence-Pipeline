import os
from services.video_renderer import VideoRenderer
from models.timeline_clip import TimelineClip
from models.video_timeline import VideoTimeline
from PIL import Image

print("\n========== IMAGE INFO ==========\n")

for path in [
    "assets/image1.jpg",
    "assets/image2.jpg",
    "assets/image3.jpg"
]:
    if os.path.exists(path):
        img = Image.open(path)
        print(f"{path} -> {img.size}")

print("\n========== BUILDING TIMELINE ==========\n")

timeline = VideoTimeline(
    clips=[
        TimelineClip(
            asset_url="assets/image1.jpg",
            duration=2.0,
            effect="none",
            caption="SCENE 1: THE UNDERDOGS"
        ),
        TimelineClip(
            asset_url="assets/image2.jpg",
            duration=2.0,
            effect="none",
            caption="SCENE 2: THE TURNING POINT"
        ),
        TimelineClip(
            asset_url="assets/image3.jpg",
            duration=2.0,
            effect="none",
            caption="SCENE 3: PURE CELEBRATION"
        )
    ]
)

for index, clip in enumerate(timeline.clips):
    print(f"Clip {index} | Asset: {clip.asset_url} | Duration: {clip.duration}s | Caption: {clip.caption}")

print("\n========== START RENDER ==========\n")

renderer = VideoRenderer(format_type="vertical", fps=30)
output = renderer.render(
    timeline,
    "output.mp4",
    audio_path="narration.wav" if os.path.exists("narration.wav") else None
)

print("\n========== FINISHED ==========\n")
print(f"Output: {output} (Size: {os.path.getsize(output)} bytes)")
