from models.video_plan import VideoPlan
from models.video_scene import VideoScene
from prompts.video_planner_prompt import VIDEO_PLANNER_PROMPT


class VideoPlannerAgent:

    def __init__(self, llm):
        self.llm = llm

    def execute(self, final_script) -> VideoPlan:
        title = getattr(final_script, "title", "Sports Documentary")
        narration = getattr(final_script, "narration", "")
        if not narration and hasattr(final_script, "body"):
            narration = f"{getattr(final_script, 'hook', '')} {final_script.body} {getattr(final_script, 'ending', '')}".strip()
        if not narration:
            narration = str(final_script)

        prompt = f"""{VIDEO_PLANNER_PROMPT}

Title:
{title}

Narration:
{narration}
"""
        plan = self.llm.generate_structured(prompt, VideoPlan)

        # Validate scenes
        if not plan.scenes:
            # Create a minimum fallback plan
            plan.scenes = [
                VideoScene(
                    start=0.0,
                    end=5.0,
                    visual_description=f"{title} football match highlight",
                    narration_segment=narration[:100],
                    caption=title
                )
            ]

        # Ensure timeline sequence is monotonic and valid
        current_time = 0.0
        validated_scenes = []
        for s in plan.scenes:
            start = max(current_time, float(s.start))
            end = max(start + 1.5, float(s.end))
            current_time = end
            validated_scenes.append(
                VideoScene(
                    start=start,
                    end=end,
                    visual_description=s.visual_description or "football match stadium action",
                    narration_segment=s.narration_segment or "",
                    caption=s.caption or title
                )
            )

        return VideoPlan(scenes=validated_scenes)
