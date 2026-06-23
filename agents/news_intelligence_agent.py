from models.evidence import Evidence


class NewsIntelligenceAgent:

    def execute(self):

        return Evidence(
            source="news",
            content=(
                "Major outlets highlight "
                "Germany's 7-1 victory "
                "and Curacao's historic goal"
            )
        )