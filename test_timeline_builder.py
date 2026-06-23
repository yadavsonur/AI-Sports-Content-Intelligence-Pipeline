from agents.timeline_builder_agent import (
    TimelineBuilderAgent
)

from models.video_plan import (
    VideoPlan
)

from models.video_scene import (
    VideoScene
)

from models.asset_collection import (
    AssetCollection
)

from models.scene_asset import (
    SceneAsset
)


video_plan = VideoPlan(
    scenes=[
        VideoScene(
            start=0,
            end=4,
            visual_description=
            "Curacao players celebrating",

            narration_segment=
            "Curacao scored their first World Cup goal",

            caption=
            "History Made"
        ),

        VideoScene(
            start=4,
            end=8,
            visual_description=
            "Germany scoring goal",

            narration_segment=
            "Germany dominated the match",

            caption=
            "7-1"
        ),

        VideoScene(
            start=8,
            end=13,
            visual_description=
            "Curacao fans cheering",

            narration_segment=
            "Fans celebrated like they had won",

            caption=
            "Pure Joy"
        )
    ]
)

asset_collection = AssetCollection(
    assets=[
        SceneAsset(
            scene_index=0,
            original_visual_description=
            "Curacao players celebrating",

            search_query=
            "curacao players celebrating",

            asset_url=
            "https://placeholder.com/curacao.jpg",

            asset_type=
            "image",

            source=
            "mock",

            title=
            "Curacao Celebration"
        ),

        SceneAsset(
            scene_index=1,
            original_visual_description=
            "Germany scoring goal",

            search_query=
            "germany scoring goal",

            asset_url=
            "https://placeholder.com/germany.jpg",

            asset_type=
            "image",

            source=
            "mock",

            title=
            "Germany Goal"
        ),

        SceneAsset(
            scene_index=2,
            original_visual_description=
            "Curacao fans cheering",

            search_query=
            "curacao fans cheering",

            asset_url=
            "https://placeholder.com/fans.jpg",

            asset_type=
            "image",

            source=
            "mock",

            title=
            "Curacao Fans"
        )
    ]
)

timeline_builder = (
    TimelineBuilderAgent()
)

timeline = (
    timeline_builder.execute(
        video_plan,
        asset_collection
    )
)

print("\n===== TIMELINE =====\n")

for clip in timeline.clips:

    print(
        f"Asset: {clip.asset_url}"
    )

    print(
        f"Duration: {clip.duration}"
    )

    print(
        f"Effect: {clip.effect}"
    )

    print(
        f"Caption: {clip.caption}"
    )

    print("-" * 40)