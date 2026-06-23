from models.evidence import Evidence


class CommunityIntelligenceAgent:

    def execute(self):

        return Evidence(
            source="community",
            content=(
                "Fans are discussing "
                "Curacao's first ever "
                "World Cup goal"
            )
        )