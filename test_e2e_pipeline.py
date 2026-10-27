import os
import shutil
import unittest
from datetime import datetime

from models.evidence import Evidence
from models.evidence_collection import EvidenceCollection
from models.chosen_story import ChosenStory
from models.video_plan import VideoPlan
from models.video_scene import VideoScene
from models.video_timeline import VideoTimeline
from models.timeline_clip import TimelineClip

from services.mock_provider import MockProvider
from services.llm_router import LLMRouter
from services.reliable_llm import ReliableLLM
from services.tts_service import TTSService
from services.video_renderer import VideoRenderer
from services.wikimedia_search_service import WikimediaSearchService
from agents.fact_verifier_agent import FactVerifierAgent
from agents.asset_collector_agent import AssetCollectorAgent
from agents.timeline_builder_agent import TimelineBuilderAgent
from graphs.content_graph import build_content_graph
from exceptions.provider_exceptions import ProviderExhausted


class TestSportsContentPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath("test_run_artifacts")
        os.makedirs(cls.test_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            try:
                shutil.rmtree(cls.test_dir)
            except Exception:
                pass

    def test_01_provider_routing_and_fallback(self):
        """Tests that LLMRouter catches ProviderExhausted and seamlessly falls back to subsequent provider."""
        exhausted_mock = MockProvider(exhaust=True)
        working_mock = MockProvider(default_response='{"status": "ok", "message": "Fallback active"}')
        router = LLMRouter([exhausted_mock, working_mock])

        resp = router.generate("test prompt")
        self.assertEqual(resp.provider, "mock")
        self.assertIn("Fallback active", resp.text)
        self.assertEqual(router.last_used_provider, "MockProvider")

    def test_02_reliable_llm_validation_retry(self):
        """Tests that ReliableLLM parses and retries structured output."""
        class SimpleModel(ChosenStory):
            pass

        mock = MockProvider()
        router = LLMRouter([mock])
        reliable = ReliableLLM(router, max_retries=2)
        result = reliable.generate_structured("editor decision request", SimpleModel)
        self.assertIsInstance(result, SimpleModel)
        self.assertTrue(len(result.headline) > 0)
        self.assertTrue(result.confidence > 0.0)

    def test_03_fact_verifier_agent(self):
        """Tests fact verification logic for supported and unsupported claims."""
        verifier = FactVerifierAgent()
        collection = EvidenceCollection(
            evidence=[
                Evidence(
                    source="match",
                    content="West Germany defeated Hungary 3-2 in 1954 World Cup final in Bern",
                    url="https://en.wikipedia.org/wiki/1954_FIFA_World_Cup_final"
                )
            ]
        )
        supported_story = ChosenStory(
            headline="West Germany 1954 World Cup final in Bern",
            reasoning="Historic comeback",
            confidence=0.95
        )
        report_pass = verifier.execute(supported_story, collection)
        self.assertEqual(report_pass["verdict"], "PASS")
        self.assertTrue(len(report_pass["verified_claims"]) >= 1)

    def test_04_offline_tts_generation_and_duration(self):
        """Tests local offline speech synthesis without cloud calls or zero durations."""
        tts = TTSService()
        out_wav = os.path.join(self.test_dir, "test_narration.wav")
        audio = tts.generate("West Germany refused to surrender in the driving rain.", out_wav)

        self.assertTrue(os.path.exists(audio.audio_path))
        self.assertTrue(os.path.getsize(audio.audio_path) > 1000)
        self.assertGreater(audio.duration, 0.5, "TTS duration must not be zero")

    def test_05_asset_collector_with_local_fixtures(self):
        """Tests asset collector with mock or local fallback fixtures."""
        collector = AssetCollectorAgent()
        plan = VideoPlan(
            scenes=[
                VideoScene(
                    start=0.0,
                    end=4.0,
                    visual_description="West Germany celebrating victory",
                    narration_segment="The celebration began.",
                    caption="Victory!"
                )
            ]
        )
        assets = collector.execute(plan)
        self.assertEqual(len(assets.assets), 1)
        self.assertTrue(assets.assets[0].title != "")
        self.assertTrue(len(assets.assets[0].license) > 0)

    def test_06_timeline_synchronization(self):
        """Tests that scene durations proportionally synchronize to measured audio duration."""
        builder = TimelineBuilderAgent()
        plan = VideoPlan(
            scenes=[
                VideoScene(start=0.0, end=10.0, visual_description="Scene 1", narration_segment="S1", caption="C1"),
                VideoScene(start=10.0, end=20.0, visual_description="Scene 2", narration_segment="S2", caption="C2"),
            ]
        )
        collector = AssetCollectorAgent()
        assets = collector.execute(plan)

        actual_audio_duration = 14.5
        timeline = builder.execute(plan, assets, target_duration=actual_audio_duration)

        total_timeline_duration = sum(c.duration for c in timeline.clips)
        self.assertAlmostEqual(total_timeline_duration, actual_audio_duration, delta=0.2)

    def test_07_video_renderer_vertical_format(self):
        """Tests that VideoRenderer produces a playable 1080x1920 MP4 with audio and captions."""
        tts = TTSService()
        audio_path = os.path.join(self.test_dir, "render_sample_audio.wav")
        audio = tts.generate("The miracle of Bern was complete.", audio_path)

        timeline = VideoTimeline(
            clips=[
                TimelineClip(
                    asset_url="assets/image1.jpg",
                    duration=audio.duration / 2.0,
                    effect="pan_left",
                    caption="SCENE 1: THE FIGHT"
                ),
                TimelineClip(
                    asset_url="assets/image2.jpg",
                    duration=audio.duration / 2.0,
                    effect="zoom_in",
                    caption="SCENE 2: THE GLORY"
                )
            ]
        )

        video_out = os.path.join(self.test_dir, "vertical_test.mp4")
        renderer = VideoRenderer(format_type="vertical", fps=30)
        rendered_file = renderer.render(timeline, video_out, audio_path=audio.audio_path)

        self.assertTrue(os.path.exists(rendered_file))
        self.assertGreater(os.path.getsize(rendered_file), 10000)

    def test_08_deterministic_end_to_end_graph(self):
        """Runs the complete 14-node LangGraph pipeline end-to-end without paid API keys."""
        mock_provider = MockProvider()
        pipeline_llm = ReliableLLM(LLMRouter([mock_provider]))
        deterministic_graph = build_content_graph(llm=pipeline_llm)

        e2e_dir = os.path.join(self.test_dir, "e2e_run")
        os.makedirs(e2e_dir, exist_ok=True)

        state = {
            "topic": "The 1954 Miracle of Bern Comeback",
            "target_duration": 30,
            "video_format": "vertical",
            "fps": 30,
            "output_dir": e2e_dir,
            "logs": []
        }

        final_state = deterministic_graph.invoke(state)

        # 1. Verify all pipeline stages executed
        self.assertIn("evidence_collection", final_state)
        self.assertGreater(len(final_state["evidence_collection"].evidence), 0)
        self.assertIn("discovery_result", final_state)
        self.assertIn("chosen_story", final_state)
        self.assertIn("fact_check", final_state)
        self.assertIn("narrative", final_state)
        self.assertIn("story_beats", final_state)
        self.assertIn("short_script", final_state)
        self.assertIn("final_script", final_state)
        self.assertIn("video_plan", final_state)
        self.assertIn("asset_collection", final_state)
        self.assertIn("narration_audio", final_state)
        self.assertIn("timeline", final_state)
        self.assertIn("rendered_video_path", final_state)
        self.assertIn("video_validation", final_state)
        self.assertIn("report_path", final_state)

        # 2. Verify Output Artifacts
        video_path = final_state["rendered_video_path"]
        self.assertTrue(os.path.exists(video_path))
        self.assertGreater(os.path.getsize(video_path), 20000)

        report_path = final_state["report_path"]
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Sports Content Intelligence Production Report", content)
            self.assertIn("Script & Commentary", content)
            self.assertIn("Research Sources", content)

        validation = final_state["video_validation"]
        self.assertEqual(validation.get("status"), "PASSED")


if __name__ == "__main__":
    unittest.main()

