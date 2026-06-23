import os

from dotenv import load_dotenv

from services.groq_provider import (
    GroqProvider
)

load_dotenv()

provider = GroqProvider(
    os.getenv(
        "GROQ_API_KEY"
    )
)

response = provider.generate(
    "Say hello in one sentence."
)

print(response)