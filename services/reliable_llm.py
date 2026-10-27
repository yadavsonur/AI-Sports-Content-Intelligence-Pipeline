from pydantic import ValidationError
from utils.json_parser import JsonParser


class ReliableLLM:

    def __init__(self, llm, max_retries: int = 3):
        self.llm = llm
        self.max_retries = max_retries

    def generate_structured(self, prompt: str, model_class):
        last_error = None
        current_prompt = prompt

        for attempt in range(self.max_retries):
            try:
                response = self.llm.generate(current_prompt)
                parsed = JsonParser.parse(response.text)
                validated = model_class(**parsed)
                return validated
            except (ValidationError, ValueError, KeyError, TypeError) as e:
                last_error = e
                print(f"[ReliableLLM] Attempt {attempt + 1}/{self.max_retries} failed validation for {model_class.__name__}: {e}")
                # Provide guidance on retry
                current_prompt = (
                    f"{prompt}\n\n"
                    f"CRITICAL: Your previous response failed with the following error:\n{e}\n"
                    f"Ensure you return ONLY valid, strictly formatted JSON adhering to the required schema."
                )

        raise RuntimeError(
            f"Failed to produce valid {model_class.__name__} after {self.max_retries} attempts"
        ) from last_error
