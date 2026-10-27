from models.evidence import Evidence
from tools.news_tool import NewsTool


class NewsIntelligenceAgent:

    def __init__(self, news_tool: NewsTool = None):
        self.news_tool = news_tool or NewsTool()

    def execute(self, topic: str = "iconic World Cup comeback") -> list[Evidence]:
        news_items = self.news_tool.get_latest(topic)
        evidence_list = []

        for item in news_items:
            content = f"{item.get('title', '')} - {item.get('summary', '')}".strip()
            evidence_list.append(
                Evidence(
                    source="news",
                    content=content or f"News reporting on {topic}",
                    url=item.get("url", "https://www.bbc.com/sport/football"),
                    metadata={"outlet": item.get("source", "news")}
                )
            )

        if not evidence_list:
            evidence_list.append(
                Evidence(
                    source="news",
                    content=f"Press media coverage of {topic}",
                    url="https://www.bbc.com/sport/football"
                )
            )

        return evidence_list
