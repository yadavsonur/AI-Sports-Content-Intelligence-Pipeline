import os
from google import genai
from configs.settings import GEMINI_MODEL_NAME
from interfaces.llm_provider import LLMProvider
from models.llm_response import LLMResponse
from services.key_pool import KeyPool
from exceptions.provider_exceptions import ProviderExhausted


class GeminiProvider(LLMProvider):

    def __init__(self, api_keys, model=None):
        clean_keys = [k for k in api_keys if k and k.strip()]
        if not clean_keys:
            raise ValueError("No valid Gemini API keys provided")
        self.key_pool = KeyPool(clean_keys)
        self.model = model or GEMINI_MODEL_NAME

    def _create_client(self, api_key):
        return genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> LLMResponse:
        initial_index = self.key_pool.current
        attempts = 0
        total_keys = len(self.key_pool.keys)

        while attempts < total_keys:
            key = self.key_pool.get_key()
            try:
                client = self._create_client(key)
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                text = response.text or ""
                return LLMResponse(
                    text=text,
                    provider="gemini",
                    model=self.model
                )
            except Exception as e:
                error_text = str(e)
                attempts += 1
                is_quota = (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "quota" in error_text.lower()
                )
                if is_quota:
                    if self.key_pool.has_next():
                        self.key_pool.next_key()
                        continue
                    else:
                        raise ProviderExhausted(f"All Gemini keys exhausted: {error_text}") from e
                raise

        raise ProviderExhausted("All Gemini keys in pool have been exhausted.")
