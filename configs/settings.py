import os

# Execution & Retry limits
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "20"))

# LLM Models
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-120b")
MODEL_NAME = GEMINI_MODEL_NAME

# Safe mode & limits
SAFE_MODE = os.getenv("SAFE_MODE", "false").lower() in ("true", "1", "yes")
DAILY_TOKEN_LIMIT = int(os.getenv("DAILY_TOKEN_LIMIT", "100000"))
MAX_RESEARCH_ITERATIONS = int(os.getenv("MAX_RESEARCH_ITERATIONS", "5"))
STORY_CONFIDENCE_THRESHOLD = float(os.getenv("STORY_CONFIDENCE_THRESHOLD", "0.85"))

# Video Defaults
DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", "60"))
DEFAULT_FPS = int(os.getenv("DEFAULT_FPS", "30"))
DEFAULT_VIDEO_FORMAT = os.getenv("DEFAULT_VIDEO_FORMAT", "vertical")  # "vertical" or "horizontal"

VERTICAL_WIDTH = 1080
VERTICAL_HEIGHT = 1920

HORIZONTAL_WIDTH = 1920
HORIZONTAL_HEIGHT = 1080

# HTTP User-Agent
USER_AGENT = "WorldCupAgent/1.0 (https://github.com/sports-intelligence; contact@example.com)"
