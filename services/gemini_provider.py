import os

from google import genai

from interfaces.llm_provider import (
    LLMProvider
)

from models.llm_response import LLMResponse
from services.key_pool import (
    KeyPool
)

from exceptions.provider_exceptions import (
    ProviderExhausted
)


class GeminiProvider(
    LLMProvider
):

    def __init__(
        self,
        api_keys
    ):

        self.key_pool = KeyPool(
            api_keys
        )

    def _create_client(
        self,
        api_key
    ):

        return genai.Client(
            api_key=api_key
        )

    def generate(
        self,
        prompt
    ):

        while True:

            key = (
                self.key_pool.get_key()
            )

            try:

                client = (
                    self._create_client(
                        key
                    )
                )

                response = (
                    client.models
                    .generate_content(
                        model=
                        "gemini-2.5-flash",
                        contents=prompt
                    )
                )

                return LLMResponse(
                    text=response.text,
                    provider="gemini",
                    model="gemini-2.5-flash"
                )

            except Exception as e:

                error_text = str(e)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    raise ProviderExhausted(
                        "Gemini unavailable"
                    )

                raise