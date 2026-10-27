import os
from models.timeline_clip import TimelineClip
from models.video_timeline import VideoTimeline


class TimelineBuilderAgent:

    def execute(self, video_plan, asset_collection, target_duration: float = None) -> VideoTimeline:
        scenes = video_plan.scenes
        assets = asset_collection.assets

        if not scenes:
            return VideoTimeline(clips=[])

        # If asset count doesn't match scenes, pad assets with available ones
        if len(assets) < len(scenes):
            fallback_asset = assets[0] if assets else None
            while len(assets) < len(scenes):
                assets.append(fallback_asset)

        # Calculate planned durations
        planned_durations = [max(1.0, float(scene.end - scene.start)) for scene in scenes]
        total_planned = sum(planned_durations)

        # Scale durations to target narration duration if provided and valid
        if target_duration and target_duration > 0 and total_planned > 0:
            scale_factor = float(target_duration) / float(total_planned)
            scaled_durations = [round(d * scale_factor, 2) for d in planned_durations]
            # Adjust rounding difference on last clip so sum is exact
            diff = round(target_duration - sum(scaled_durations), 2)
            if scaled_durations:
                scaled_durations[-1] = max(1.0, round(scaled_durations[-1] + diff, 2))
        else:
            scaled_durations = planned_durations

        clips = []
        for scene, asset, duration in zip(scenes, assets, scaled_durations):
            # Prefer valid local path for MoviePy rendering
            image_source = ""
            if asset:
                if asset.local_path and os.path.exists(asset.local_path):
                    image_source = asset.local_path
                elif asset.asset_url and os.path.exists(asset.asset_url):
                    image_source = asset.asset_url
                else:
                    image_source = asset.local_path or asset.asset_url

            # Fallback to local repo asset if missing
            if not image_source or not os.path.exists(image_source):
                candidates = ["assets/image1.jpg", "assets/image2.jpg", "assets/image3.jpg", "assets/aad.jpg"]
                image_source = next((c for c in candidates if os.path.exists(c)), "assets/image1.jpg")

            clip = TimelineClip(
                asset_url=image_source,
                duration=duration,
                effect=self._choose_effect(duration),
                caption=scene.caption
            )
            clips.append(clip)

        return VideoTimeline(clips=clips)

    def _choose_effect(self, duration: float) -> str:
        if duration >= 5.0:
            return "zoom_in"
        elif duration >= 3.0:
            return "pan_left"
        return "none"
