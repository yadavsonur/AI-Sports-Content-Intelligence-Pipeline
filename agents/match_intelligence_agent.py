from models.evidence import Evidence


class MatchIntelligenceAgent:

    def execute(self):

        return Evidence(
            source="match",
            content=(
                "Germany defeated Curacao 7-1 "
                "in World Cup opener"
            )
        )