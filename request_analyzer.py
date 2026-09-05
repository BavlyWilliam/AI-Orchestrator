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

    understanding_score: int = Field(
        description=(
            "How well the user's request is "
            "understood, from 0 to 100."
        ),
        ge=0,
        le=100
    )

    needs_clarification: bool = Field(
        description=(
            "True only when missing information "
            "materially affects the ability to "
            "complete the user's request."
        )
    )

    clarification_question: str | None = Field(
        description=(
            "The single most important question "
            "to ask if clarification is needed. "
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
            "Estimated complexity based on reasoning "
            "difficulty, requirements, and number "
            "of steps."
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
            "Prompt components that are meaningfully "
            "missing and would improve the request."
        )
    )

    analysis_reason: str = Field(
        description=(
            "Brief explanation of why the request "
            "does or does not need clarification."
        )
    )


# =====================================
# GEMINI CLIENT
# =====================================

def get_client():
    """
    Create a Gemini client using the API key
    stored in the environment.
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

    Gemini returns a structured response
    matching the RequestAnalysis schema.
    """

    if not isinstance(
        user_request,
        str
    ) or not user_request.strip():

        raise ValueError(
            "user_request must be a "
            "non-empty string."
        )

    client = get_client()

    analysis_prompt = f"""
You are the request analysis component of
an AI orchestration system.

Analyze the user's request and determine:

1. How well you understand the user's intent.
2. Whether clarification is genuinely necessary.
3. The single most important clarification
   question if one is required.
4. The primary task category.
5. The complexity.
6. Which prompt components are meaningfully
   missing:
   - context
   - role
   - task
   - output
   - format
7. A brief explanation of your reasoning.

Important rules:

- Do not ask for information that is unnecessary
  to produce a useful answer.
- Broad requests can still be valid requests.
- Prefer reasonable assumptions when they would
  not materially change the result.
- Ask a clarification question only when missing
  information would materially affect the result.
- Return only one clarification question.
- Do not treat words such as "no", "nothing",
  "stop", or similar words as cancellation commands.
  Analyze their meaning in context.
- Do not rely on keyword matching.
- Judge the meaning of the complete request.

User request:

{user_request}
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
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
