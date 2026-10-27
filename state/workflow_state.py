from typing import Any, Dict, List, Optional, TypedDict
from models.asset_collection import AssetCollection
from models.chosen_story import ChosenStory
from models.evidence_collection import EvidenceCollection
from models.final_script import FinalScript
from models.narration_audio import NarrationAudio
from models.narrative import Narrative
from models.short_script import ShortScript
from models.story_beats import StoryBeats
from models.story_discovery_result import StoryDiscoveryResult
from models.video_plan import VideoPlan
from models.video_timeline import VideoTimeline


class WorkflowState(TypedDict, total=False):
    # Pipeline inputs
    topic: str
    target_duration: int
    video_format: str  # "vertical" (1080x1920) or "horizontal" (1920x1080)
    fps: int
    output_dir: str

    # Research & Intelligence
    evidence_collection: EvidenceCollection
    stories: List[Any]

    # Discovery & Editorial
    discovery_result: StoryDiscoveryResult
    chosen_story: ChosenStory
    editor_decision: Any

    # Fact-checking
    fact_check: Dict[str, Any]

    # Story generation & Script
    narrative: Narrative
    story_beats: StoryBeats
    short_script: ShortScript
    final_script: FinalScript
    script: str

    # Video Planning & Assets
    video_plan: VideoPlan
    asset_collection: AssetCollection

    # Audio & Synchronization
    narration_audio: NarrationAudio
    timeline: VideoTimeline

    # Rendering & Validation
    rendered_video_path: str
    video_validation: Dict[str, Any]
    report_path: str

    # Execution telemetry
    logs: List[str]
    error: Optional[str]
