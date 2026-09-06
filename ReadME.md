<div align="center">

# AI-Orchestrator

### From user request to the best LLM recommendation

An AI orchestration project that analyzes a user's request, identifies task requirements and constraints, enhances prompts when useful, uses benchmark evidence, and recommends the most suitable AI model or AI assistant.

**Request Analysis · Clarification · Prompt Enhancement · Benchmark Data · Model Recommendation · SQLite History**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

</div>

---

## The Problem

With hundreds of LLMs and AI assistants available, choosing the right model for a specific task is becoming a problem of its own.

AI-Orchestrator is designed to reduce that guesswork by analyzing what the user actually needs, identifying important requirements and constraints, using benchmark evidence when available, and producing an explainable recommendation.

---

## How It Works

![AI-Orchestrator Architecture](docs/Screenshots/architecture.png)

AI-Orchestrator moves from understanding the user's request to evaluating available AI options and producing a recommendation.

The project is built around modular stages so that the decision-making process remains understandable and expandable.

---

# Features

## Request Analysis

The system analyzes the user's request to identify:

- Task category
- Complexity
- Important requirements
- Constraints
- Missing critical information
- Whether clarification is genuinely necessary

The goal is to understand the meaning of the request rather than rely entirely on simple keyword matching.

---

## Clarification and Validation

When important information is missing, the system can ask a focused clarification question.

The design philosophy is to avoid unnecessary clarification and use reasonable defaults whenever possible.

---

## Prompt Enhancement

The project can improve and structure a user's prompt while preserving the original intent.

The prompt enhancement process aims to:

- Improve clarity
- Preserve requirements
- Avoid inventing information
- Produce a more structured request when useful

---

## Prompt Scoring

The enhanced prompt is evaluated using detectable prompt components such as:

- Context
- Role
- Task
- Output
- Format

This provides a simple quality signal and helps identify missing components.

---

## Benchmark-Informed Recommendations

The project retrieves benchmark data through the benchmark provider and uses relevant signals as evidence during model evaluation.

Depending on the task, the recommendation process can consider:

- Model capabilities
- Benchmark scores
- Pricing data
- Context length
- Latency and speed
- Task requirements

Benchmark data is treated as evidence rather than an automatic ranking system.

---

## Smart Model Recommendation

The recommendation process evaluates available AI options based on the user's actual request.

Factors can include:

- Task type
- Complexity
- Reasoning requirements
- Coding requirements
- Cost and speed considerations
- Microsoft ecosystem relevance
- Product fit
- Available benchmark evidence

The goal is not simply to recommend the highest-ranked model.

The goal is to recommend the **most suitable model for the specific task**.

---

# Demo

The screenshots below show different parts of the project during development and execution.

## Project Workflow

![Project Workflow](<docs/Screenshots/Screenshot 2026-09-05 211411.png>)

## Request Analysis and Processing

![Request Analysis](<docs/Screenshots/Screenshot 2026-09-06 003138.png>)

## Model and Benchmark Evaluation

![Model Evaluation](<docs/Screenshots/Screenshot 2026-09-06 005240.png>)

## Recommendation Results

![Recommendation Results](<docs/Screenshots/Screenshot 2026-09-06 021407.png>)

## Additional Project Screenshots

![Project Screenshot](<docs/Screenshots/Screenshot 2026-09-06 134626.png>)

![Project Screenshot](<docs/Screenshots/Screenshot 2026-09-06 134817.png>)

> Screenshots are stored directly in `docs/Screenshots/` and referenced using their exact filenames.

---

# Architecture

The project currently consists of the following modules:

| File | Responsibility |
|---|---|
| `main.py` | Entry point that coordinates the application workflow |
| `request_analyzer.py` | Analyzes requests and identifies task requirements |
| `model_recommender.py` | Evaluates and recommends suitable AI models |
| `benchmark_provider.py` | Retrieves and prepares benchmark data |
| `prompt_enhancer.py` | Improves prompts while preserving user intent |
| `prompt_scorer.py` | Evaluates prompt components |
| `database.py` | Manages SQLite storage |
| `validator.py` | Supports request validation logic |
| `Knowledge/general_sop.md` | Project knowledge and supporting documentation |

---

# Database

The project uses SQLite to store the history of orchestration activity.

Stored information can include:

- User requests
- Analysis results
- Model recommendations
- Prompt enhancements
- Interactions
- Timestamps

The database provides an auditable record of how requests move through the system.

---

# Project Structure

```text
AI-Orchestrator/
│
├── Knowledge/
│   └── general_sop.md
│
├── docs/
│   └── Screenshots/
│       ├── architecture.png
│       ├── Screenshot 2026-09-05 211411.png
│       ├── Screenshot 2026-09-06 003138.png
│       ├── Screenshot 2026-09-06 005240.png
│       ├── Screenshot 2026-09-06 021407.png
│       ├── Screenshot 2026-09-06 134626.png
│       └── Screenshot 2026-09-06 134817.png
│
├── .env
├── .gitignore
├── benchmark_provider.py
├── database.py
├── LICENSE
├── main.py
├── model_recommender.py
├── orchestrator.db
├── prompt_enhancer.py
├── prompt_scorer.py
├── README.md
├── request_analyzer.py
└── validator.py
```

---

# Requirements

- Python 3.x
- Gemini API key
- Artificial Analysis API key for benchmark retrieval

The project uses environment variables for API credentials.

Create a local `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
ARTIFICIAL_ANALYSIS_API_KEY=your_artificial_analysis_api_key
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/BavlyWilliam/AI-Orchestrator.git
cd AI-Orchestrator
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### Windows PowerShell

```bash
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

Install the project's required Python packages:

```bash
pip install google-genai python-dotenv pydantic requests
```

---

# Running the Project

Run:

```bash
python main.py
```

Example request:

```text
Help me debug a Python script that is failing to connect to a SQLite database.
```

The system then analyzes the request and moves it through the orchestration workflow.

---

# Testing Philosophy

The project should be tested with different types of requests.

### Clear Request

```text
Write a Python script that organizes files.
```

Expected behavior:

- No unnecessary clarification
- Correct task classification
- Appropriate recommendation

### Broad but Usable Request

```text
Create a marketing plan for a coffee shop.
```

Expected behavior:

- Use reasonable defaults
- Avoid automatically asking multiple questions

### Ambiguous Request

```text
Help me with my project.
```

Expected behavior:

- Recognize that important information is missing
- Ask a focused clarification question when necessary

---

# Current Development Status

The current project includes:

- Request analysis
- Clarification handling
- Prompt enhancement
- Prompt scoring
- Benchmark retrieval
- Model recommendation
- SQLite request and interaction history

---

# Future Development

Possible future improvements include:

- More automated testing
- Expanded benchmark sources
- Configurable recommendation rules
- More supported AI models
- Cost-aware recommendations
- Speed versus quality modes
- Provider API routing
- Recommendation performance evaluation

The project is intentionally being developed incrementally.

---

# Design Philosophy

> AI orchestration should make meaningful decisions based on the user's actual request, not just keyword matching or arbitrary scores.

The project prioritizes:

- Explainable decisions
- Modular architecture
- Small focused components
- Minimal unnecessary clarification
- Benchmark evidence without blind ranking
- Readability
- Maintainability
- Incremental development

---

# Security

API keys are loaded from environment variables.

**Never commit your `.env` file or `orchestrator.db` if it contains real request data.**

Before making the repository public, verify:

```bash
git status
git log --all -- .env
git log --all -- orchestrator.db
```

---

# License

This project is licensed under the MIT License.

Built independently by **Bavly William**.
