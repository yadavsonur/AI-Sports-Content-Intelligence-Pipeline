from models.evidence import Evidence
from tools.reddit_tool import RedditTool


class CommunityIntelligenceAgent:

    def __init__(self, reddit_tool: RedditTool = None):
        self.reddit_tool = reddit_tool or RedditTool()

    def execute(self, topic: str = "iconic World Cup comeback") -> list[Evidence]:
        discussions = self.reddit_tool.search(topic)
        evidence_list = []

        for disc in discussions:
            content = f"{disc.get('title', '')} ({disc.get('sentiment', '')}): {disc.get('content', '')}".strip()
            evidence_list.append(
                Evidence(
                    source="community",
                    content=content or f"Fan discussion on {topic}",
                    url=disc.get("url", "https://www.reddit.com/r/soccer"),
                    metadata={"source_board": disc.get("source", "community")}
                )
            )

        if not evidence_list:
            evidence_list.append(
                Evidence(
                    source="community",
                    content=f"Global supporter sentiment regarding {topic}",
                    url="https://www.reddit.com/r/soccer"
                )
            )

        return evidence_list
