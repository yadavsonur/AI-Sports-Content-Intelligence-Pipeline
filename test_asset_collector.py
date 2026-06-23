from agents.asset_collector_agent import (
    AssetCollectorAgent
)

from models.video_plan import (
    VideoPlan
)

from models.video_scene import (
    VideoScene
)

plan = VideoPlan(
    scenes=[
        VideoScene(
            start=0,
            end=5,
            visual_description=
            "Curacao players celebrating",

            narration_segment=
            "Historic moment",

            caption=
            "History made"
        ),

        VideoScene(
            start=5,
            end=10,
            visual_description=
            "Germany scoring goal",

            narration_segment=
            "Germany dominate",

            caption=
            "7-1"
        )
    ]
)

collector = (
    AssetCollectorAgent()
)

result = (
    collector.execute(plan)
)

print(result)