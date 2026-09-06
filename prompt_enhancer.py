import os

from dotenv import load_dotenv
from google import genai


# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()


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
# PROMPT ENHANCER
# =====================================

def enhance_prompt(
    user_request,
    analysis_result
):
    """
    Use Gemini to improve and structure the
    user's request while preserving their intent.

    The enhancer must not invent requirements or
    ask unnecessary clarification questions.
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

    enhancement_prompt = f"""
You are the prompt enhancement component of an AI
orchestration system.

Your job is to transform the user's request into a
clearer and more useful prompt for another AI model.

You have already received an analysis of the request.
Use that analysis to improve the prompt intelligently.

USER REQUEST:

{user_request}


REQUEST ANALYSIS:

Task Category:
{analysis_result.task_category}

Complexity:
{analysis_result.complexity}

Understanding Score:
{analysis_result.understanding_score}

Missing Components:
{", ".join(analysis_result.missing_components) if analysis_result.missing_components else "None"}

Analysis Reason:
{analysis_result.analysis_reason}


IMPORTANT RULES:

1. Preserve the user's original intent.

2. Do not invent requirements, facts, preferences,
   constraints, or details that the user did not provide.

3. Do not ask the user questions.

4. Do not add artificial prompt-engineering sections
   such as "Role", "Format", or "Output" unless they
   genuinely improve the prompt for this specific task.

5. Do not mechanically react to the missing components.

6. Missing "format" does NOT automatically mean you
   should add formatting instructions.

7. Missing "role" does NOT automatically mean you
   should assign the AI a role.

8. Use reasonable assumptions only when they would not
   materially change the result.

9. If clarification information is already included in
   the user request, incorporate it naturally.

10. Make the final prompt clear, focused, and useful for
    the task category.

11. The enhanced prompt should be ready to send directly
    to another AI model.

12. Do not explain what you changed.

13. Return ONLY the enhanced prompt.
"""

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=enhancement_prompt
    )

    if not interaction.output_text:
        raise RuntimeError(
            "Gemini returned an empty enhanced prompt."
        )

    return interaction.output_text.strip()
