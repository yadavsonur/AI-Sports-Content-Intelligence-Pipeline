import os
from dotenv import load_dotenv

load_dotenv()

# Safely collect Gemini keys from environment
GEMINI_KEYS = [
    k.strip()
    for k in [
        os.getenv("GEMINI_KEY_1"),
        os.getenv("GEMINI_KEY_2"),
        os.getenv("GEMINI_KEY_3"),
        os.getenv("GEMINI_API_KEY"),
    ]
    if k and k.strip() and not k.strip().startswith("KEY_")
]

# Safely collect Groq keys from environment
GROQ_KEYS = [
    k.strip()
    for k in [
        os.getenv("GROQ_API_KEY"),
        os.getenv("GROQ_KEY_1"),
    ]
    if k and k.strip() and not k.strip().startswith("KEY_")
]

OPENROUTER_KEYS = [
    k.strip()
    for k in [
        os.getenv("OPENROUTER_API_KEY"),
    ]
    if k and k.strip() and not k.strip().startswith("KEY_")
]
