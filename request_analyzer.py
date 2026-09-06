import os
from typing import Literal

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()


# =====================================
# STRUCTURED ANALYSIS RESULT
# =====================================

class RequestAnalysis(BaseModel):
    """
    Structured result returned by Gemini
    after analyzing a user request.
    """

    is_actionable_request: bool = Field(
        description=(
            "Whether the user's input contains a real "
            "task, goal, question, or request that the "
            "orchestration system can process. Greetings, "
            "dismissals, insults without a request, and "
            "meaningless input should be false."
        )
    )

    understanding_score: int = Field(
        description=(
            "How actionable and sufficiently specified "
            "the user's request is for the orchestration "
            "system, from 0 to 100. A non-actionable "
            "input should receive a very low score."
        ),
        ge=0,
        le=100
    )

    needs_clarification: bool = Field(
        description=(
            "True only when missing information materially "
            "affects the ability to complete the user's "
            "request usefully."
        )
    )

    clarification_question: str | None = Field(
        description=(
            "Ask exactly one focused question that collects "
            "the single most important missing piece of "
            "information. Do not combine multiple questions. "
            "Use null when clarification is not needed."
        )
    )

    task_category: Literal[
        "coding",
        "debugging",
        "writing",
        "research",
        "data_analysis",
        "creative_work",
        "automation",
        "learning",
        "other"
    ] = Field(
        description=(
            "The primary type of task the user "
            "is requesting."
        )
    )

    complexity: Literal[
        "simple",
        "medium",
        "complex"
    ] = Field(
        description=(
            "Estimated complexity based on technical "
            "difficulty, reasoning requirements, "
            "requirements, and number of steps."
        )
    )

    missing_components: list[
        Literal[
            "context",
            "role",
            "task",
            "output",
            "format"
        ]
    ] = Field(
        description=(
            "Components that are meaningfully missing from "
            "the request. Do not mark a component as missing "
            "just because it is absent from the wording. "
            "Only include it when its absence materially "
            "limits understanding or execution."
        )
    )

    analysis_reason: str = Field(
        description=(
            "Brief explanation of why the request is or is "
            "not actionable and why clarification is or is "
            "not needed."
        )
    )


# =====================================
# GEMINI CLIENT
# =====================================

def get_client():
    """
    Create a Gemini client using the API key
    stored in the .env file.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Check your .env file."
        )

    return genai.Client(
        api_key=api_key
    )


# =====================================
# REQUEST ANALYZER
# =====================================

def analyze_request(user_request):
    """
    Analyze a user request using Gemini.

    Returns:
        RequestAnalysis:
            A structured analysis of the request.
    """

    if (
        not isinstance(user_request, str)
        or not user_request.strip()
    ):
        raise ValueError(
            "user_request must be a "
            "non-empty string."
        )

    client = get_client()

    analysis_prompt = f"""
You are the request analysis component of an AI
orchestration system.

Analyze the user's input and determine:

1. Whether the input contains an actionable request.
2. How actionable and sufficiently specified the request is.
3. Whether clarification is genuinely necessary.
4. The single most important clarification question,
   if clarification is required.
5. The primary task category.
6. The estimated complexity.
7. Which components are meaningfully missing.
8. A brief explanation of your reasoning.

Important definitions:

ACTIONABLE REQUEST:

An actionable request contains a meaningful task,
goal, question, instruction, or problem that an AI
system can reasonably attempt to help with.

Examples:

"Create an Access database"
→ actionable

"Help me debug my Python code"
→ actionable

"I want to buy a laptop"
→ actionable

"Fuck off"
→ not actionable

"Hello"
→ not actionable unless it includes a request

"Nothing"
→ usually not actionable when used as the user's
entire input

UNDERSTANDING SCORE:

The understanding score measures how ready the
request is for useful processing.

Do not give a high score simply because you
understand what the user means.

Examples:

"Create an Access database"
→ actionable but underspecified

"Create an Access database for managing inventory"
→ more sufficiently specified

A non-actionable input should receive a very
low score.

CLARIFICATION RULES:

- Do not ask for information unnecessarily.

- Broad requests can still be valid and useful.

- Prefer reasonable assumptions when they would
  not materially change the result.

- Ask for clarification only when missing
  information would materially affect the result.

- Ask exactly ONE focused clarification question.

- Ask for the SINGLE most important missing piece
  of information.

- Do not ask artificial prompt-engineering questions
  such as:
    "What format do you want?"
    "What role should the AI take?"
    "What output do you want?"

  unless the user's actual task genuinely requires
  that information.

- Do not ask multiple questions in one sentence.

- Use null for clarification_question when
  needs_clarification is false.

MISSING COMPONENTS:

Possible components are:

- context
- role
- task
- output
- format

Only mark a component as missing when it meaningfully
affects understanding or execution.

Do NOT mechanically mark role or format as missing
just because the user did not explicitly provide them.

For example:

"Write an email apologizing for missing a meeting"

This does not necessarily need:
- role
- format
- clarification

The system can reasonably infer an appropriate format.

GENERAL RULES:

- Do not rely on keyword matching.

- Judge the meaning of the complete input.

- Do not treat words such as "no", "nothing",
  "stop", or similar words as cancellation commands.

- Analyze their meaning in context.

- Do not invent user requirements.

User input:

{user_request}
"""

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=analysis_prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": RequestAnalysis.model_json_schema()
        }
    )

    if not interaction.output_text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return RequestAnalysis.model_validate_json(
        interaction.output_text
    )


# =====================================
# TEMPORARY TEST
# =====================================

if __name__ == "__main__":

    test_request = input(
        "Enter a request to analyze:\n> "
    ).strip()

    try:

        result = analyze_request(
            test_request
        )

        print(
            "\n--- Gemini Analysis ---"
        )

        print(
            result.model_dump_json(
                indent=2
            )
        )

    except Exception as error:

        print(
            f"\nError: {error}"
        )
