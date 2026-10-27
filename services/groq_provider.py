import os
from groq import Groq
from configs.settings import GROQ_MODEL_NAME
from interfaces.llm_provider import LLMProvider
from models.llm_response import LLMResponse
from exceptions.provider_exceptions import ProviderExhausted


class GroqProvider(LLMProvider):

    FALLBACK_MODELS = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
    ]

    def __init__(self, api_key: str, model: str = None):
        if not api_key or not api_key.strip():
            raise ValueError("No valid Groq API key provided")
        self.api_key = api_key.strip()
        self.client = Groq(api_key=self.api_key, timeout=25.0)
        self.model = model or GROQ_MODEL_NAME

    def generate(self, prompt: str) -> LLMResponse:
        models_to_try = [self.model] + [m for m in self.FALLBACK_MODELS if m != self.model]
        last_error = None

        for current_model in models_to_try:
            try:
                completion = self.client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.7,
                )
                text = completion.choices[0].message.content or ""
                return LLMResponse(
                    text=text,
                    provider="groq",
                    model=current_model,
                )
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "model_not_found" in err_str or "404" in err_str:
                    # Model not available on this tier/key, try next model in fallback list
                    continue
                if "429" in err_str or "rate_limit" in err_str or "quota" in err_str or "exhausted" in err_str:
                    raise ProviderExhausted(f"Groq rate limit/quota reached: {e}") from e
                raise

        raise ProviderExhausted(f"Groq failed across all models: {last_error}") from last_error
