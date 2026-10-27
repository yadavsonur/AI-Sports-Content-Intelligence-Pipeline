import os
import json
from datetime import datetime
from langgraph.graph import StateGraph, START, END

from state.workflow_state import WorkflowState
from models.evidence_collection import EvidenceCollection
from agents.match_intelligence_agent import MatchIntelligenceAgent
from agents.news_intelligence_agent import NewsIntelligenceAgent
from agents.community_intelligence_agent import CommunityIntelligenceAgent
from tools.search_tool import SearchTool
from agents.story_discovery_agent import StoryDiscoveryAgent
from agents.editor_agent import EditorAgent
from agents.fact_verifier_agent import FactVerifierAgent
from agents.narrative_agent import NarrativeAgent
from agents.story_beats_agent import StoryBeatsAgent
from agents.writer_agent import WriterAgent
from agents.sports_commentator_agent import SportsCommentatorAgent
from agents.video_planner_agent import VideoPlannerAgent
from agents.asset_collector_agent import AssetCollectorAgent
from agents.timeline_builder_agent import TimelineBuilderAgent
from services.wikimedia_search_service import WikimediaSearchService
from services.tts_service import TTSService
from services.video_renderer import VideoRenderer
from services.reliable_llm import ReliableLLM
from services.llm_router import LLMRouter
from services.gemini_provider import GeminiProvider
from services.groq_provider import GroqProvider
from services.mock_provider import MockProvider
from configs.providers import GEMINI_KEYS, GROQ_KEYS
from configs.settings import DEFAULT_DURATION, DEFAULT_FPS, DEFAULT_VIDEO_FORMAT


def get_default_llm():
    """
    Builds the production LLM stack with available Gemini and Groq providers.
    Falls back gracefully to MockProvider if no API keys are present.
    """
    providers = []
    if GEMINI_KEYS:
        try:
            providers.append(GeminiProvider(GEMINI_KEYS))
        except Exception as e:
            print(f"[GraphInit] Warning initializing Gemini provider: {e}")

    if GROQ_KEYS:
        try:
            providers.append(GroqProvider(GROQ_KEYS[0]))
        except Exception as e:
            print(f"[GraphInit] Warning initializing Groq provider: {e}")

    if not providers:
        print("[GraphInit] No external LLM keys configured. Using offline MockProvider.")
        providers.append(MockProvider())

    router = LLMRouter(providers)
    return ReliableLLM(router)


def build_content_graph(llm=None):
    active_llm = llm or get_default_llm()

    # Instantiate agents
    match_agent = MatchIntelligenceAgent()
    news_agent = NewsIntelligenceAgent()
    community_agent = CommunityIntelligenceAgent()
    search_tool = SearchTool()

    discovery_agent = StoryDiscoveryAgent(active_llm)
    editor_agent = EditorAgent(active_llm)
    fact_agent = FactVerifierAgent(active_llm)
    narrative_agent = NarrativeAgent(active_llm)
    beats_agent = StoryBeatsAgent(active_llm)
    writer_agent = WriterAgent(active_llm)
    commentator_agent = SportsCommentatorAgent(active_llm)
    planner_agent = VideoPlannerAgent(active_llm)
    timeline_builder = TimelineBuilderAgent()
    tts_service = TTSService()

    # --- Node Definitions ---

    def research_node(state: WorkflowState) -> dict:
        topic = state.get("topic") or "An iconic FIFA World Cup comeback"
        logs = state.get("logs", [])
        logs.append(f"Starting research on topic: {topic}")
        print(f"\n[1/12 Research] Investigating topic: '{topic}'")

        evidence_items = []
        # 1. Match records
        try:
            match_evidence = match_agent.execute(topic)
            evidence_items.extend(match_evidence)
        except Exception as e:
            logs.append(f"Match intelligence error: {e}")

        # 2. News reports
        try:
            news_evidence = news_agent.execute(topic)
            evidence_items.extend(news_evidence)
        except Exception as e:
            logs.append(f"News intelligence error: {e}")

        # 3. Community discussions
        try:
            comm_evidence = community_agent.execute(topic)
            evidence_items.extend(comm_evidence)
        except Exception as e:
            logs.append(f"Community intelligence error: {e}")

        # 4. Search tool verification
        try:
            search_records = search_tool.search(topic)
            from models.evidence import Evidence
            for s in search_records:
                evidence_items.append(
                    Evidence(
                        source=s.get("source", "search"),
                        content=f"{s.get('title', '')}: {s.get('snippet', '')}",
                        url=s.get("url", ""),
                        metadata={"title": s.get("title", "")}
                    )
                )
        except Exception as e:
            logs.append(f"Search tool error: {e}")

        collection = EvidenceCollection(evidence=evidence_items)
        print(f"[Research] Collected {len(collection.evidence)} verified evidence items across sources.")
        return {
            "evidence_collection": collection,
            "logs": logs
        }

    def discovery_node(state: WorkflowState) -> dict:
        collection = state["evidence_collection"]
        print("\n[2/12 Discovery] Discovering story candidates and hypotheses...")
        result = discovery_agent.execute(collection)
        print(f"[Discovery] Best story hypothesis: {result.best_story}")
        return {
            "discovery_result": result,
            "stories": [h.model_dump() for h in result.hypotheses]
        }

    def editorial_node(state: WorkflowState) -> dict:
        discovery_result = state["discovery_result"]
        print("\n[3/12 Editorial] Evaluating editorial merit and audience retention...")
        chosen = editor_agent.execute(discovery_result)
        print(f"[Editorial] Selected story: '{chosen.headline}' (confidence: {chosen.confidence})")
        return {
            "chosen_story": chosen,
            "editor_decision": chosen
        }

    def fact_verification_node(state: WorkflowState) -> dict:
        chosen = state["chosen_story"]
        collection = state["evidence_collection"]
        print("\n[4/12 Fact-Checking] Cross-verifying factual claims against research records...")
        fact_check = fact_agent.execute(chosen, collection)
        print(f"[Fact-Check] Verdict: {fact_check.get('verdict')} (Confidence: {fact_check.get('confidence')})")
        return {
            "fact_check": fact_check
        }

    def narrative_node(state: WorkflowState) -> dict:
        chosen = state["chosen_story"]
        collection = state["evidence_collection"]
        print("\n[5/12 Narrative] Crafting emotional arc and turning points...")
        narrative = narrative_agent.execute(chosen, collection)
        print(f"[Narrative] Protagonist: {narrative.protagonist} | Turning Point: {narrative.turning_point}")
        return {
            "narrative": narrative
        }

    def story_beats_node(state: WorkflowState) -> dict:
        chosen = state["chosen_story"]
        narrative = state["narrative"]
        print("\n[6/12 Story Beats] Structuring hook, setup, twist, reveal, and payoff...")
        beats = beats_agent.execute(chosen, narrative)
        print(f"[Story Beats] Hook: '{beats.hook}'")
        return {
            "story_beats": beats
        }

    def scriptwriting_node(state: WorkflowState) -> dict:
        chosen = state["chosen_story"]
        narrative = state["narrative"]
        beats = state["story_beats"]
        print("\n[7/12 Scriptwriting] Writing short-form narrative script...")
        script = writer_agent.execute(chosen, narrative, beats)
        full_text = f"{script.hook} {script.body} {script.ending}".strip()
        return {
            "short_script": script,
            "script": full_text
        }

    def commentary_node(state: WorkflowState) -> dict:
        short_script = state["short_script"]
        print("\n[8/12 Commentary] Polishing commentary for documentary cadence...")
        final_script = commentator_agent.execute(short_script)
        print(f"[Commentary] Title: '{final_script.title}' ({len(final_script.narration.split())} words)")
        return {
            "final_script": final_script,
            "script": final_script.narration
        }

    def video_planning_node(state: WorkflowState) -> dict:
        final_script = state["final_script"]
        print("\n[9/12 Video Planning] Constructing scene-by-scene storyboard...")
        plan = planner_agent.execute(final_script)
        print(f"[Video Plan] Generated {len(plan.scenes)} storyboard scenes.")
        return {
            "video_plan": plan
        }

    def asset_collection_node(state: WorkflowState) -> dict:
        plan = state["video_plan"]
        output_dir = state.get("output_dir") or "runs/latest"
        media_dir = os.path.join(output_dir, "media")
        os.makedirs(media_dir, exist_ok=True)

        print("\n[10/12 Asset Collection] Searching and downloading media assets from Wikimedia...")
        search_svc = WikimediaSearchService(download_dir=media_dir)
        collector = AssetCollectorAgent(image_search_service=search_svc)
        collection = collector.execute(plan)
        print(f"[Asset Collection] Collected {len(collection.assets)} assets with license attribution.")
        return {
            "asset_collection": collection
        }

    def tts_narration_node(state: WorkflowState) -> dict:
        final_script = state["final_script"]
        output_dir = state.get("output_dir") or "runs/latest"
        audio_path = os.path.join(output_dir, "narration.wav")

        print("\n[11/12 TTS Narration] Generating speech via local offline engine...")
        narration_text = final_script.narration
        audio = tts_service.generate(narration_text, audio_path)
        print(f"[TTS] Narration audio generated: {audio.audio_path} (Duration: {audio.duration:.2f}s)")
        return {
            "narration_audio": audio
        }

    def timeline_sync_node(state: WorkflowState) -> dict:
        plan = state["video_plan"]
        assets = state["asset_collection"]
        audio = state["narration_audio"]

        print(f"\n[Synchronizing Timeline] Synchronizing {len(plan.scenes)} scenes to audio duration ({audio.duration:.2f}s)...")
        timeline = timeline_builder.execute(plan, assets, target_duration=audio.duration)
        total_timeline = sum(c.duration for c in timeline.clips)
        print(f"[Timeline] Synchronized: {len(timeline.clips)} clips | Total duration: {total_timeline:.2f}s")
        return {
            "timeline": timeline
        }

    def video_rendering_node(state: WorkflowState) -> dict:
        timeline = state["timeline"]
        audio = state["narration_audio"]
        output_dir = state.get("output_dir") or "runs/latest"
        video_format = state.get("video_format") or DEFAULT_VIDEO_FORMAT
        fps = state.get("fps") or DEFAULT_FPS
        video_out = os.path.join(output_dir, "final_video.mp4")

        print(f"\n[12/12 Video Rendering] Rendering {video_format} video at {fps} FPS...")
        renderer = VideoRenderer(format_type=video_format, fps=fps)
        rendered_path = renderer.render(timeline, video_out, audio_path=audio.audio_path)
        print(f"[Video Rendering] Output saved to: {rendered_path}")
        return {
            "rendered_video_path": rendered_path
        }

    def validation_and_report_node(state: WorkflowState) -> dict:
        output_dir = state.get("output_dir") or "runs/latest"
        rendered_path = state.get("rendered_video_path")
        audio = state.get("narration_audio")
        timeline = state.get("timeline")
        evidence_col = state.get("evidence_collection")
        fact_check = state.get("fact_check", {})
        final_script = state.get("final_script")
        asset_col = state.get("asset_collection")
        video_format = state.get("video_format") or DEFAULT_VIDEO_FORMAT
        fps = state.get("fps") or DEFAULT_FPS

        # Validate video file
        validation = {
            "file_exists": False,
            "file_size_bytes": 0,
            "duration": 0.0,
            "format": video_format,
            "fps": fps,
            "status": "FAILED",
            "error": None
        }

        if rendered_path and os.path.exists(rendered_path):
            size = os.path.getsize(rendered_path)
            validation["file_exists"] = True
            validation["file_size_bytes"] = size
            if size > 10000:
                validation["status"] = "PASSED"
                if timeline and timeline.clips:
                    validation["duration"] = round(sum(c.duration for c in timeline.clips), 2)
            else:
                validation["error"] = f"File size too small: {size} bytes"
        else:
            validation["error"] = f"Rendered video file not found at {rendered_path}"

        # Generate Comprehensive Report
        report_md_path = os.path.join(output_dir, "production_report.md")
        report_json_path = os.path.join(output_dir, "production_report.json")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "topic": state.get("topic"),
            "video_format": video_format,
            "target_duration": state.get("target_duration", DEFAULT_DURATION),
            "validation": validation,
            "fact_checking": fact_check,
            "script": {
                "title": final_script.title if final_script else "",
                "narration": final_script.narration if final_script else "",
                "hashtags": final_script.hashtags if final_script else []
            },
            "sources": [
                {
                    "source": e.source,
                    "content": e.content,
                    "url": e.url
                }
                for e in (evidence_col.evidence if evidence_col else [])
            ],
            "media_assets": [
                {
                    "scene_index": a.scene_index,
                    "description": a.original_visual_description,
                    "query": a.search_query,
                    "local_path": a.local_path,
                    "remote_url": a.asset_url,
                    "license": a.license,
                    "attribution": a.attribution
                }
                for a in (asset_col.assets if asset_col else [])
            ],
            "outputs": {
                "final_video": rendered_path,
                "narration_audio": audio.audio_path if audio else "",
                "report_markdown": report_md_path,
                "report_json": report_json_path
            }
        }

        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        # Markdown format report
        md_content = f"""# Sports Content Intelligence Production Report

**Generated:** {report_data['timestamp']}  
**Topic:** {report_data['topic']}  
**Status:** {validation['status']}  
**Video Output:** `{rendered_path}`  
**Video Specs:** {video_format} ({validation.get('duration', 0)}s @ {fps}fps, {round(validation.get('file_size_bytes', 0) / (1024*1024), 2)} MB)

---

## 1. Script & Commentary
### {final_script.title if final_script else 'Documentary Script'}
> {final_script.narration if final_script else ''}

**Tags:** {' '.join(final_script.hashtags if final_script else [])}

---

## 2. Fact-Checking & Claim Verification
- **Verdict:** {fact_check.get('verdict', 'N/A')}
- **Confidence Score:** {fact_check.get('confidence', 0)}
- **Verified Claims:** {len(fact_check.get('verified_claims', []))}
- **Flagged Claims:** {len(fact_check.get('flagged_claims', []))}

---

## 3. Research Sources & Evidence
| Source | Verified Content | URL |
|---|---|---|
"""
        for s in report_data["sources"][:8]:
            content_snippet = s["content"][:120].replace("\n", " ")
            md_content += f"| {s['source']} | {content_snippet}... | [{s['url']}]({s['url']}) |\n"

        md_content += """
---

## 4. Media Assets & Licensing Attribution
| Scene | Query | Local File | License | Attribution |
|---|---|---|---|---|
"""
        for a in report_data["media_assets"]:
            local_basename = os.path.basename(a["local_path"]) if a["local_path"] else "fixture"
            md_content += f"| {a['scene_index']} | {a['query']} | `{local_basename}` | {a['license']} | {a['attribution']} |\n"

        md_content += f"""
---
*Produced autonomously by AI Sports Content Intelligence Pipeline.*
"""
        with open(report_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"\n[Validation & Reporting] Production Report generated at: {report_md_path}")
        return {
            "video_validation": validation,
            "report_path": report_md_path
        }

    # --- Build StateGraph ---
    workflow = StateGraph(WorkflowState)

    workflow.add_node("research", research_node)
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("editorial", editorial_node)
    workflow.add_node("fact_verification", fact_verification_node)
    workflow.add_node("narrative", narrative_node)
    workflow.add_node("story_beats", story_beats_node)
    workflow.add_node("scriptwriting", scriptwriting_node)
    workflow.add_node("commentary", commentary_node)
    workflow.add_node("video_planning", video_planning_node)
    workflow.add_node("asset_collection", asset_collection_node)
    workflow.add_node("tts_narration", tts_narration_node)
    workflow.add_node("timeline_sync", timeline_sync_node)
    workflow.add_node("video_rendering", video_rendering_node)
    workflow.add_node("validation_and_report", validation_and_report_node)

    # Sequential edges connecting the full pipeline
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "discovery")
    workflow.add_edge("discovery", "editorial")
    workflow.add_edge("editorial", "fact_verification")
    workflow.add_edge("fact_verification", "narrative")
    workflow.add_edge("narrative", "story_beats")
    workflow.add_edge("story_beats", "scriptwriting")
    workflow.add_edge("scriptwriting", "commentary")
    workflow.add_edge("commentary", "video_planning")
    workflow.add_edge("video_planning", "asset_collection")
    workflow.add_edge("asset_collection", "tts_narration")
    workflow.add_edge("tts_narration", "timeline_sync")
    workflow.add_edge("timeline_sync", "video_rendering")
    workflow.add_edge("video_rendering", "validation_and_report")
    workflow.add_edge("validation_and_report", END)

    return workflow.compile()


# Standard default graph instance
graph = build_content_graph()

