from interfaces.llm_provider import (
    LLMProvider
)

from exceptions.provider_exceptions import (
    ProviderExhausted
)


class MockProvider(
    LLMProvider
):

    def generate(
        self,
        prompt
    ):

        raise ProviderExhausted(
            "Mock exhausted"
        )