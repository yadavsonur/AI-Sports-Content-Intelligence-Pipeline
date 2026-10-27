from models.evidence import Evidence
from services.football_data_service import FootballDataService


class MatchIntelligenceAgent:

    def __init__(self, data_service: FootballDataService = None):
        self.data_service = data_service or FootballDataService()

    def execute(self, topic: str = "iconic World Cup comeback") -> list[Evidence]:
        records = self.data_service.get_match_intelligence(topic)
        evidence_list = []

        for r in records:
            content = f"{r.get('title', '')}: {r.get('facts', '')}".strip()
            evidence_list.append(
                Evidence(
                    source="match",
                    content=content or f"Match intelligence for {topic}",
                    url=r.get("url", "https://en.wikipedia.org/wiki/FIFA_World_Cup"),
                    metadata={"competition": r.get("competition", "FIFA World Cup")}
                )
            )

        if not evidence_list:
            evidence_list.append(
                Evidence(
                    source="match",
                    content=f"Tournament match intelligence regarding {topic}",
                    url="https://en.wikipedia.org/wiki/FIFA_World_Cup"
                )
            )

        return evidence_list
