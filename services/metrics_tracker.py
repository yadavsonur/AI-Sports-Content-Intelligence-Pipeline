class MetricsTracker:

    def __init__(self):

        self.total_calls = 0

        self.provider_usage = {}

    def record(
        self,
        provider
    ):

        self.total_calls += 1

        self.provider_usage[
            provider
        ] = (
            self.provider_usage
            .get(provider, 0)
            + 1
        )

    def summary(self):

        return {
            "total_calls":
                self.total_calls,

            "provider_usage":
                self.provider_usage
        }