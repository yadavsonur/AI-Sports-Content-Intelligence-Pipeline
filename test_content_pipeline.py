from agents import story_beats_agent
from agents.story_discovery_agent import (
    StoryDiscoveryAgent
)

from agents.sports_commentator_agent import (
    SportsCommentatorAgent)

from agents.editor_agent import (
    EditorAgent
)

from agents.narrative_agent import (
    NarrativeAgent  )

from agents.writer_agent import (
    WriterAgent
)

from models.evidence import Evidence
from models.evidence_collection import (
    EvidenceCollection
)

from services.gemini_provider import (
    GeminiProvider
)

from services.reliable_llm import (
    ReliableLLM
)

from services.groq_provider import (
    GroqProvider  )

from services.llm_router import (
    LLMRouter
)

from agents.video_planner_agent import (
    VideoPlannerAgent
)

import os
from dotenv import load_dotenv

load_dotenv()

router = LLMRouter(
    [
        GeminiProvider(
            [
                os.getenv(
                    "GEMINI_KEY_1"
                )
            ]
        ),

        GroqProvider(
            os.getenv(
                "GROQ_API_KEY"
            )
        )
    ]
)

llm = ReliableLLM(
    router
)


discovery_agent = (
    StoryDiscoveryAgent(llm)
)

editor_agent = (
    EditorAgent(llm)
)

writer_agent = (
    WriterAgent(llm)
)

story_beats_agent = (
    story_beats_agent.StoryBeatsAgent(llm)
)

narrative_agent = (
    NarrativeAgent(llm)                 
)

sports_commentary_agent = (
    SportsCommentatorAgent(llm)     
)

video_planner = VideoPlannerAgent(
    llm
)

collection = EvidenceCollection(
    evidence=[
        Evidence(
            source="match",
            content="Germany defeated Curacao 7-1"
        ),
        Evidence(
            source="community",
            content="Fans celebrate Curacao's first World Cup goal"
        ),
        Evidence(
            source="news",
            content="Media highlight Curacao's historic moment"
        )
    ]
)

story_result = discovery_agent.execute(
    collection
)

print("\n===== DISCOVERY =====\n")
print(story_result)

chosen_story = editor_agent.execute(
    story_result
)

print("\n===== STORY =====\n")
print(chosen_story)

narrative = narrative_agent.execute(
    chosen_story,
    collection
)

print("\n===== NARRATIVE =====\n")
print(narrative)

story_beats = story_beats_agent.execute(
    chosen_story,
    narrative
)
print("\n===== STORY BEATS =====\n")
print(story_beats)

script = writer_agent.execute(
    chosen_story,
    narrative,
    story_beats
)

print("\n===== SCRIPT =====\n")
print(script)

commentary = sports_commentary_agent.execute(
    script
)
print("\n===== COMMENTARY =====\n")
print(commentary)   

video_plan = video_planner.execute(
    commentary
)

print("\n===== VIDEO PLAN =====\n")
print(video_plan)