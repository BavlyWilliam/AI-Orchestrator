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
            "How actionable and sufficiently "
            "specified the user's request is for "
            "the orchestration system, from 0 to 100. "
            "A non-request, dismissal, greeting, "
            "or meaningless input should receive "
            "a low score."
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
            "Ask exactly one focused question that "
            "collects the single most important missing "
            "piece of information. Do not combine "
            "multiple questions. Use null when "
            "clarification is not needed."
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
            "Prompt components that are meaningfully "
            "missing and could improve the request."
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

1. How actionable and sufficiently specified the
   request is.
2. Whether clarification is genuinely necessary.
3. The single most important clarification question
   if clarification is required.
4. The primary task category.
5. The estimated complexity.
6. Which prompt components are meaningfully missing:
   - context
   - role
   - task
   - output
   - format
7. A brief explanation of your reasoning.

Important rules:

- Understanding score means how actionable and
  sufficiently specified the input is as a request
  that the orchestration system can process.

- Do not give a high understanding score simply
  because you understand the meaning of the input.

- Greetings, dismissals, insults without a request,
  meaningless input, or statements with no actionable
  task should receive a low understanding score.

- Do not ask for information that is unnecessary
  to produce a useful answer.

- Broad requests can still be valid requests.

- Prefer reasonable assumptions when they would not
  materially change the result.

- Ask for clarification only when missing information
  would materially affect the result.

- Ask exactly one focused clarification question.

- A clarification question must request only ONE
  missing piece of information.

- Do not combine multiple questions or ask for
  multiple pieces of information in one question.

- Use null for clarification_question when
  needs_clarification is false.

- Do not treat words such as "no", "nothing",
  "stop", or similar words as cancellation commands.
  Analyze their meaning in context.

- Do not rely on keyword matching.

- Judge the meaning of the complete input.

User input:

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
