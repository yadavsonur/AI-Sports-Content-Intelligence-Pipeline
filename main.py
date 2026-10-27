import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

from configs.settings import DEFAULT_DURATION, DEFAULT_FPS, DEFAULT_VIDEO_FORMAT
from graphs.content_graph import build_content_graph, graph
from services.mock_provider import MockProvider
from services.reliable_llm import ReliableLLM
from services.llm_router import LLMRouter


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Sports Content Intelligence Pipeline - Autonomous Short-Form Video Generator"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="An iconic FIFA World Cup comeback",
        help="Sports documentary topic or match event (default: 'An iconic FIFA World Cup comeback')"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help=f"Target video duration in seconds (default: {DEFAULT_DURATION})"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["vertical", "horizontal"],
        default=DEFAULT_VIDEO_FORMAT,
        help="Video orientation format: 'vertical' (1080x1920) or 'horizontal' (1920x1080) (default: vertical)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=DEFAULT_FPS,
        help=f"Video frames per second (default: {DEFAULT_FPS})"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Destination directory for output artifacts (default: runs/run_YYYYMMDD_HHMMSS)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in deterministic offline mock mode (no external LLM API calls)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Create organized run output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir or os.path.abspath(f"runs/run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print(" AI SPORTS CONTENT INTELLIGENCE PIPELINE")
    print("=" * 70)
    print(f"Topic:           {args.topic}")
    print(f"Target Duration: {args.duration}s")
    print(f"Format:          {args.format.upper()} ({args.fps} FPS)")
    print(f"Output Directory:{output_dir}")
    print(f"Mode:            {'OFFLINE MOCK' if args.mock else 'LIVE PRODUCTION'}")
    print("=" * 70)

    # Configure graph runner
    if args.mock:
        print("[Pipeline] Initializing with deterministic offline mock provider...")
        mock_router = LLMRouter([MockProvider()])
        pipeline_llm = ReliableLLM(mock_router)
        active_graph = build_content_graph(llm=pipeline_llm)
    else:
        active_graph = graph

    # Initial pipeline state
    initial_state = {
        "topic": args.topic,
        "target_duration": args.duration,
        "video_format": args.format,
        "fps": args.fps,
        "output_dir": output_dir,
        "logs": []
    }

    start_time = datetime.now()

    try:
        result = active_graph.invoke(initial_state)

        elapsed = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 70)
        print(" PIPELINE EXECUTION COMPLETE")
        print("=" * 70)
        print(f"Elapsed Time:      {elapsed:.1f} seconds")

        validation = result.get("video_validation", {})
        print(f"Validation Status: {validation.get('status', 'N/A')}")
        print(f"Final Video File:  {result.get('rendered_video_path')}")
        print(f"Narration Audio:   {result.get('narration_audio', {}).audio_path if hasattr(result.get('narration_audio'), 'audio_path') else 'Generated'}")
        print(f"Production Report: {result.get('report_path')}")
        print("=" * 70)

        if validation.get("status") == "PASSED":
            print("\nSUCCESS: Video generation and validation finished successfully!")
            sys.exit(0)
        else:
            print(f"\nWARNING: Video validation flagged issue: {validation.get('error')}")
            sys.exit(0)

    except Exception as e:
        print(f"\n[FATAL ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
