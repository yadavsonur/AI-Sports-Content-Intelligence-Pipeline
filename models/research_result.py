from pydantic import BaseModel

from models.story_candidate import StoryCandidate


class ResearchResult(BaseModel):

    match_stories: list[StoryCandidate] = []

    news_stories: list[StoryCandidate] = []

    community_stories: list[StoryCandidate] = []

    trend_stories: list[StoryCandidate] = []

    merged_stories: list[StoryCandidate] = []