from exceptions.provider_exceptions import ProviderExhausted
from models.llm_response import LLMResponse


class LLMRouter:

    def __init__(self, providers: list):
        if not providers:
            raise ValueError("LLMRouter requires at least one provider")
        self.providers = providers
        self.last_used_provider = None

    def generate(self, prompt: str) -> LLMResponse:
        last_error = None

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            try:
                response = provider.generate(prompt)
                self.last_used_provider = provider_name
                return response
            except ProviderExhausted as e:
                print(f"[LLMRouter] Provider {provider_name} exhausted/unavailable: {e}. Trying fallback...")
                last_error = e
                continue
            except Exception as e:
                print(f"[LLMRouter] Provider {provider_name} unexpected failure: {e}. Trying fallback...")
                last_error = e
                continue

        raise RuntimeError(f"All LLM providers ({len(self.providers)}) failed or were exhausted: {last_error}") from last_error
