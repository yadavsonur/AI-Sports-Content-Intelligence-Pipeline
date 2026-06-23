from groq import Groq

from interfaces.llm_provider import (
    LLMProvider
)

from models.llm_response import (
    LLMResponse
)


class GroqProvider(
    LLMProvider
):

    def __init__(
        self,
        api_key
    ):

        self.client = Groq(
            api_key=api_key
        )

    def generate(
        self,
        prompt
    ):

        completion = (
            self.client.chat.completions.create(
                model=
                "llama-3.3-70b-versatile",

                messages=[
                    {
                        "role":
                        "user",

                        "content":
                        prompt
                    }
                ],

                temperature=0.7
            )
        )

        text = (
            completion
            .choices[0]
            .message
            .content
        )

        return LLMResponse(
            text=text,
            provider="groq",
            model=
            "llama-3.3-70b-versatile"
        )