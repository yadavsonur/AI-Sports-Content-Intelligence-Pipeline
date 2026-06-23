from models.timeline_clip import (
    TimelineClip
)

from models.video_timeline import (
    VideoTimeline
)


class TimelineBuilderAgent:

    def execute(
        self,
        video_plan,
        asset_collection
    ):

        clips = []

        for scene, asset in zip(
            video_plan.scenes,
            asset_collection.assets
        ):

            duration = (
                scene.end -
                scene.start
            )

            clip = TimelineClip(
                asset_url=
                asset.asset_url,

                duration=
                duration,

                effect=
                self._choose_effect(
                    scene
                ),

                caption=
                scene.caption
            )

            clips.append(
                clip
            )

        return VideoTimeline(
            clips=clips
        )

    def _choose_effect(
        self,
        scene
    ):

        duration = (
            scene.end -
            scene.start
        )

        if duration >= 5:
            return "zoom_in"

        return "pan_left"