import json
import re


class JsonParser:

    @staticmethod
    def parse(text: str):
        """
        Extract JSON from LLM responses.

        Handles:
        - ```json ... ```
        - ``` ... ```
        - Raw JSON
        - Extra text before/after JSON
        """

        if not text:
            raise ValueError("Empty response received")

        text = text.strip()

        # Remove markdown fences
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        text = text.strip()

        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Extract first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "No JSON object found in response"
            )

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON: {e}"
            ) from e