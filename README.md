# AI-Orchestrator

An AI orchestration system that analyzes a user's request, determines its task requirements and complexity, improves the request when useful, and recommends the most suitable AI model or AI assistant.

The project combines LLM-based request analysis with live benchmark data and stores the complete request lifecycle in a SQLite database.

**LLM-powered request analysis · Live benchmark-informed recommendations · Prompt enhancement · SQLite request history**

![Python](https://img.shields.io/badge/python-3.x-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## Features

### **LLM-Powered Request Analysis**

Uses Gemini to analyze the meaning of a user's request rather than relying entirely on keyword matching.

The analyzer determines:

* Whether the request is actionable
* How sufficiently specified the request is
* Whether clarification is genuinely necessary
* The most important clarification question, when needed
* The primary task category
* Estimated complexity
* Meaningfully missing request components

The system is designed to avoid unnecessary clarification questions and use reasonable assumptions when possible.

### **Focused Clarification Handling**

When critical information is missing, the system asks **one focused clarification question** rather than overwhelming the user with multiple questions.

The clarification process is limited to a maximum number of attempts to prevent endless clarification loops.

### **Prompt Enhancement**

Once a request is understood, Gemini transforms it into a clearer and more structured prompt.

The prompt enhancer:

* Preserves the user's original intent
* Does not invent requirements
* Does not ask additional questions
* Avoids unnecessary prompt-engineering templates
* Produces a prompt ready to send to another AI model

### **Prompt Quality Scoring**

The enhanced prompt is evaluated against five detectable components:

* Context
* Role
* Task
* Output
* Format

The scoring system provides a simple quality signal and identifies components that were not detected.

### **Benchmark-Informed Model Recommendations**

The system fetches current benchmark data from Artificial Analysis when an API key is available.

Relevant benchmark signals include:

* Intelligence index
* Coding index
* Mathematics index
* Model pricing data
* Output speed

The benchmark data is provided to the recommendation engine as evidence rather than being treated as an automatic ranking system.

If benchmark data is unavailable, the recommendation process can continue without it.

### **Smart AI Model Recommendation**

The system currently recommends from:

* ChatGPT
* Claude Sonnet
* Claude Opus
* Gemini Flash
* Gemini Pro
* Microsoft Copilot

Each option receives a compatibility score from **0–100** based on the user's request.

The recommendation considers factors such as:

* Task type
* Complexity
* Reasoning requirements
* Coding requirements
* Microsoft ecosystem relevance
* Product fit
* Available benchmark evidence

The system does not automatically recommend the most powerful model.

### **SQLite Request History**

Every request is stored in a local SQLite database.

The system records:

* Original user request
* Clarification questions and answers
* Request analysis results
* Enhanced prompts
* Prompt quality scores
* Task categories
* Final model recommendations
* Recommendation reasons
* Request status

This creates an auditable history of how the orchestration system processed each request.

---

## Current Workflow

```text
User Request
      │
      ▼
Request Analysis
      │
      ├── Is the request actionable?
      │
      ├── Is clarification genuinely needed?
      │
      ▼
Focused Clarification (if required)
      │
      ▼
Prompt Enhancement
      │
      ▼
Prompt Quality Scoring
      │
      ▼
Live Benchmark Retrieval
      │
      ▼
AI Model Recommendation
      │
      ▼
SQLite Storage
```

---

## Requirements

* Python 3.x
* Gemini API key
* Artificial Analysis API key for live benchmark data

Python dependencies currently include:

* `google-genai`
* `python-dotenv`
* `pydantic`
* `requests`

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd AI-Orchestrator
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows PowerShell:**

```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install google-genai python-dotenv pydantic requests
```

### 4. Create a `.env` file

```env
GEMINI_API_KEY=your_gemini_api_key
ARTIFICIAL_ANALYSIS_API_KEY=your_artificial_analysis_api_key
```

> The Artificial Analysis API key is optional for the recommendation workflow. If benchmark data cannot be retrieved, the system continues without live benchmark data.

---

## Running the Project

```bash
python main.py
```

The application will ask:

```text
What would you like help with?
>
```

Enter a request and the system will process it through the orchestration pipeline.

Example:

```text
Help me debug a Python script that is failing to connect to a SQLite database.
```

---

## Example Output Flow

The system processes a request through the following stages:

```text
--- Gemini Request Analysis ---

Understanding Score: 85/100
Task Category: debugging
Complexity: medium
```

```text
--- Enhanced Prompt ---

[Improved version of the user's request]
```

```text
--- Prompt Quality Score ---

Total Score: 80/100
```

```text
--- AI Recommendations ---

Claude Sonnet
Compatibility: 92/100

Gemini Pro
Compatibility: 88/100

ChatGPT
Compatibility: 84/100
```

The exact recommendations depend on the request and available benchmark data.

---

## Architecture

The project separates orchestration stages into focused modules so that the decision-making process remains understandable and testable.

### Component Map

| Component          | Path                    | Role                                                                                              |
| ------------------ | ----------------------- | ------------------------------------------------------------------------------------------------- |
| Entry Point        | `main.py`               | Coordinates the complete orchestration workflow                                                   |
| Request Analyzer   | `request_analyzer.py`   | Uses Gemini to analyze actionability, clarity, task category, complexity, and clarification needs |
| Prompt Enhancer    | `prompt_enhancer.py`    | Improves the request while preserving user intent                                                 |
| Prompt Scorer      | `prompt_scorer.py`      | Detects context, role, task, output, and format components                                        |
| Model Recommender  | `model_recommender.py`  | Recommends AI models and assistants based on task compatibility                                   |
| Benchmark Provider | `benchmark_provider.py` | Retrieves live benchmark data from Artificial Analysis                                            |
| Database Layer     | `database.py`           | Manages SQLite storage and request history                                                        |
| Legacy Validator   | `validator.py`          | Earlier rule-based request validation logic retained during development                           |

---

## Model Recommendation Strategy

The project intentionally avoids a simple rule such as:

> "Claude is best for coding."

Instead, the recommendation process analyzes the meaning of the request and considers the actual requirements.

For example:

* A simple writing task does not automatically require the most powerful model.
* Coding benchmarks matter more for coding-related requests.
* Reasoning and intelligence benchmarks matter more for complex analytical tasks.
* Microsoft Copilot receives special consideration for Microsoft ecosystem workflows.
* ChatGPT is treated as a user-facing product recommendation rather than a directly selectable OpenAI model.
* Benchmark scores are considered evidence, not absolute truth.

The goal is to recommend the **most suitable option for the specific task**, not simply the highest-ranked model.

---

## Benchmark Data

When available, the project retrieves current model data from Artificial Analysis.

The current implementation matches supported AI options with relevant models in the Artificial Analysis dataset and extracts benchmark information used by the recommendation engine.

Benchmark data is used to support recommendations rather than replace semantic reasoning.

Benchmark data attribution:

Artificial Analysis

https://artificialanalysis.ai/

---

## Database

The project uses SQLite for local request history.

### `requests`

Stores the primary orchestration request.

Fields include:

* Original prompt
* Final request after clarification
* Creation timestamp
* Understanding score
* Clarification status
* Prompt score
* Enhanced prompt
* Task category
* Recommended AI option
* Recommendation reason
* Processing status

### `interactions`

Stores events associated with a request.

Examples include:

* User request
* Clarification question
* Clarification answer
* Cancellation
* Empty clarification response

Each interaction is linked to its parent request through a foreign key.

### Relationship

```text
requests
   │
   │ 1
   │
   ▼
interactions
   │
   │ many
```

A single request can contain multiple interactions.

---

## Project Structure

```text
AI-Orchestrator/
│
├── main.py
├── request_analyzer.py
├── prompt_enhancer.py
├── prompt_scorer.py
├── model_recommender.py
├── benchmark_provider.py
├── database.py
├── validator.py
│
├── .gitignore
│
├── .env                 # Create locally; do not commit
└── orchestrator.db      # Generated locally; do not commit
```

---

## Testing

The project is currently being developed iteratively.

The recommendation system should be tested with different types of requests, including:

### Clear Request

```text
Write a Python script that organizes files.
```

Expected behavior:

* No unnecessary clarification
* Correct task classification
* Appropriate model recommendation

### Broad but Usable Request

```text
Create a marketing plan for a coffee shop.
```

Expected behavior:

* Process the request without automatically asking multiple questions
* Use reasonable assumptions

### Ambiguous Request

```text
Help me with my project.
```

Expected behavior:

* Recognize that critical context is missing
* Ask one focused clarification question

### Microsoft Ecosystem Request

```text
Help me create a complex Excel dashboard.
```

Expected behavior:

* Give Microsoft Copilot meaningful consideration
* Consider whether ecosystem integration provides an advantage

---

## Current Development Status

The project currently supports:

* LLM-based request analysis
* Focused clarification handling
* Prompt enhancement
* Prompt component scoring
* Live benchmark retrieval
* AI model compatibility scoring
* SQLite request and interaction history

### Planned Development

Future development may include:

* Structured automated test suites
* Expanded benchmark sources
* Configurable recommendation strategies
* More supported models and AI products
* Model performance evaluation
* Provider routing and execution
* Cost-aware recommendation modes
* Recommendation performance tracking

The project is intentionally being developed incrementally.

The goal is to build an understandable orchestration foundation before adding unnecessary frameworks, multi-agent systems, or complex infrastructure.

---

## Design Philosophy

AI-Orchestrator is built around a simple principle:

> AI orchestration should make meaningful decisions based on the user's actual request, not just keyword matching or arbitrary scores.

The project prioritizes:

* Explainable decisions
* Modular architecture
* Small focused components
* Minimal unnecessary clarification
* Benchmark evidence without blind ranking
* Practical product fit
* Incremental development
* Readability and maintainability

---

## License

This project is licensed under the MIT License.

Built independently by **Bavly William**.
