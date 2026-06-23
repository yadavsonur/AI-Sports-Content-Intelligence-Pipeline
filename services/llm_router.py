from exceptions.provider_exceptions import (
    ProviderExhausted
)


class LLMRouter:

    def __init__(
        self,
        providers
    ):

        self.providers = providers

    def generate(
        self,
        prompt
    ):

        last_error = None

        for provider in self.providers:

            try:

                return provider.generate(
                    prompt
                )

            except ProviderExhausted as e:

                print(
                    f"{provider.__class__.__name__}"
                    " exhausted"
                )

                last_error = e

        raise RuntimeError(
            "All providers exhausted"
        ) from last_error