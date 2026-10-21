# AI Sports Content Intelligence Pipeline ⚽

An AI-powered Python project for turning sports research into structured, story-driven content. The repository brings together specialized agent modules, an LLM provider layer, research and story models, and video/audio utilities to support an automated sports-content workflow.

The current executable entry point invokes a **LangGraph** workflow that runs a researcher, editor, and writer in sequence. Additional modules explore match and news intelligence, story discovery, narrative building, asset collection, timeline planning, sports commentary, text-to-speech, and video rendering.

## Overview

The goal of this project is to help transform sports information into a content package that can be reviewed and developed into a short-form video.

**High-level workflow**

```text
Sports research
      ↓
Editorial selection
      ↓
Script / content generation
      ↓
Supporting research, story and media modules
      ↓
Audio and video utilities
```

The exact end-to-end behavior depends on the currently wired graph and configuration. In the present entry point, `main.py` calls the compiled graph in `graphs/content_graph.py`, whose active path is **researcher → editor → writer**.

## Features and modules

- **Agent-based workflow:** a LangGraph state graph coordinates the current researcher, editor, and writer stages.
- **Sports research and intelligence modules:** separate agent modules cover match intelligence, news intelligence, community intelligence, and story discovery.
- **Story development:** modules for narrative generation, story beats, timeline building, and sports commentary.
- **LLM provider abstraction:** Gemini and Groq provider implementations return a shared response model.
- **Provider routing and key handling:** an LLM router can try configured providers in order; a key-pool utility supports API-key selection for provider calls.
- **Asset discovery:** image-search interfaces and services include Wikimedia-oriented search support.
- **Audio generation:** a text-to-speech service uses gTTS.
- **Video rendering:** a MoviePy renderer composes image scenes and captions into a 1280×720 MP4 at 24 FPS.
- **Structured data models:** Pydantic-style/domain model modules represent stories, evidence, scripts, assets, scenes, timelines, and research state.
- **Tests and experiments:** the repository contains test scripts for pipeline components, provider behavior, timeline building, TTS, and video rendering.

Some modules are scaffolding or work in progress. For example, the current `WorldCupService` methods are placeholders, so the README does not claim live World Cup data retrieval is implemented.

## Tech stack

| Area | Technology |
| --- | --- |
| Language | Python |
| Agent orchestration | LangGraph |
| LLM integration | Google Gen AI SDK (Gemini), Groq |
| Text-to-speech | gTTS |
| Video generation | MoviePy |
| Media encoding | FFmpeg (required by typical MoviePy video workflows) |
| Asset discovery | Search-service interfaces, including Wikimedia search |
| Data modeling | Shared Python model classes |
| Testing | Python test scripts |

## Repository structure

```text
.
├── agents/       # Research, editing, writing, narrative, story and media agents
├── configs/      # Provider and workflow settings
├── exceptions/   # Provider-related exceptions
├── graphs/       # LangGraph workflow definition
├── interfaces/   # Provider and image-search interfaces
├── metrics/      # Agent metrics
├── models/       # Structured workflow, story, script and media models
├── prompts/      # Agent-specific prompts
├── services/     # LLM providers, routing, search, TTS and video rendering
├── state/        # Research and workflow state definitions
├── storage/      # Checkpoint management
├── tools/        # Search, news and Reddit tools
├── utils/        # Parsing and specialist routing utilities
├── main.py       # Application entry point
└── test_*.py     # Component and pipeline tests
```

## Getting started

### Prerequisites

- Python 3.10 or a compatible version for the installed dependencies
- Git
- API credentials for the LLM provider(s) you intend to use
- FFmpeg installed and available on your system PATH for video rendering

### 1. Clone the repository

```bash
git clone https://github.com/yadavsonur/AI-Sports-Content-Intelligence-Pipeline.git
cd AI-Sports-Content-Intelligence-Pipeline
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

The repository currently does not include a dependency lockfile or a `requirements.txt`. Install the packages required by the modules you plan to run, including the relevant LLM SDKs and media libraries.

For the core components, dependencies include packages such as:

```bash
pip install langgraph google-genai groq moviepy gTTS
```

Other modules may require additional packages. If you are setting up the full pipeline, inspect the imports in the agents, services, tools, and tests and record the verified environment in a requirements file.

### 4. Configure API credentials

Do not put real API keys in source files or commit them to Git. The provider configuration file, `configs/providers.py`, currently contains placeholder values and should be replaced with a secure configuration approach before running real provider calls.

For local development, environment variables are a safer starting point. For example:

**PowerShell**
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
$env:GROQ_API_KEY="your-groq-api-key"
```

**macOS / Linux**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GROQ_API_KEY="your-groq-api-key"
```

These variable names are examples for your local setup; update the provider initialization/configuration to read the environment variables consistently. Never commit real credentials.

### 5. Run the application

```bash
python main.py
```

The entry point invokes the compiled graph with an initially empty state. Successful execution depends on the researcher/editor/writer nodes' required inputs, provider setup, and any external services they call.

## Running tests

The repository contains standalone test scripts. You can run an individual test with:

```bash
python test_content_pipeline.py
```

Other test files cover areas such as provider behavior, asset search, timeline building, TTS, and video rendering. Review each script before running it: some tests may call external APIs, need credentials, or create media files.

## Video rendering notes

The MoviePy renderer composes image assets with text captions, then exports an MP4 at 1280×720 and 24 FPS. The renderer currently sets `audio=False`; generated narration is handled separately by the TTS service and is not automatically mixed into the rendered video by this renderer.

Make sure you have the rights to use any source images, footage, audio, logos, or other media in generated content. Respect each source's license and attribution requirements, and verify sports-media usage rights before publishing.

## Configuration and development notes

- `configs/settings.py` defines settings such as the model name, retry count, research iteration limit, token limit, and story-confidence threshold.
- The active graph is defined in `graphs/content_graph.py`. Adding an agent file does not automatically add it to the execution path; wire it into the graph to make it part of the active workflow.
- Provider routing depends on how provider instances are configured and passed to the router.
- Before using the pipeline for publication, validate source reliability, dates, match facts, player names, quotes, and generated claims. Treat generated output as a draft that needs editorial review.
- Avoid presenting unverified AI-generated commentary as a factual report.

## Roadmap ideas

- Standardize dependencies and add a pinned `requirements.txt` or `pyproject.toml`.
- Load API credentials from environment variables and document provider setup in one place.
- Add structured logging, retries, and provider health/cost metrics.
- Wire research, source validation, asset collection, story planning, TTS, and video rendering into a tested end-to-end graph.
- Add source citations and a fact-checking gate before scripts are published.
- Add integration tests using mocked providers and deterministic fixtures.

## Author

**Sonu Yadav**  
GitHub: [@yadavsonur](https://github.com/yadavsonur)

---

This project is under active development. Features described as modules or utilities may not yet be connected into a single end-to-end production workflow.
