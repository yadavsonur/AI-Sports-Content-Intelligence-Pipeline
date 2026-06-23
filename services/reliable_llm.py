from urllib import response

from pydantic import ValidationError

from utils.json_parser import JsonParser


class ReliableLLM:

    def __init__(
        self,
        llm,
        max_retries=3
    ):

        self.llm = llm
        self.max_retries = max_retries

    def generate_structured(
        self,
        prompt,
        model_class
    ):

        last_error = None

        for attempt in range(
            self.max_retries
        ):

            try:

                response = self.llm.generate(
                    prompt
                )

                print(
                    f"\nProvider: "
                    f"{response.provider}"
                )

                print(
                    f"Model: "
                    f"{response.model}"
                )

                parsed = JsonParser.parse(
                    response.text
                )

                validated = model_class(
                    **parsed
                )

                return validated

            except (
                ValidationError,
                ValueError,
                KeyError
            ) as e:

                last_error = e

                print(
                    f"Attempt {attempt + 1} failed"
                )

        raise RuntimeError(
            f"Failed after "
            f"{self.max_retries} retries"
        ) from last_error