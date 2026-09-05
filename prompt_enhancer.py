def enhance_prompt(user_request):
    """
    Create a structured Version 1 enhanced prompt.

    This is currently rule-based.
    An LLM-powered enhancement system will be added later.
    """

    enhanced_prompt = f"""
You are an expert assistant.

User Request:
{user_request}

Your task is to understand the user's request and provide
the most helpful response possible.

If information is missing, make reasonable assumptions
and clearly state those assumptions.

Provide a clear and accurate answer.

Use a structured format with clear sections when appropriate.
"""

    return enhanced_prompt.strip()
