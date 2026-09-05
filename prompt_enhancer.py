def enhance_prompt(
    user_request,
    missing_components=None
):
    """
    Create a structured enhanced prompt.

    The enhancement adapts based on
    prompt components that were not
    detected during scoring.
    """

    if missing_components is None:

        missing_components = []

    instructions = []

    # ---------------------------------
    # CONTEXT
    # ---------------------------------

    if "context" in missing_components:

        instructions.append(
            "If important context is missing, "
            "make reasonable assumptions and "
            "clearly state them."
        )

    # ---------------------------------
    # ROLE
    # ---------------------------------

    if "role" in missing_components:

        instructions.append(
            "Use the most appropriate expertise "
            "for the user's request."
        )

    # ---------------------------------
    # TASK
    # ---------------------------------

    if "task" in missing_components:

        instructions.append(
            "First determine the user's intended "
            "task before responding."
        )

    # ---------------------------------
    # OUTPUT
    # ---------------------------------

    if "output" in missing_components:

        instructions.append(
            "Provide a complete and useful answer "
            "that directly addresses the request."
        )

    # ---------------------------------
    # FORMAT
    # ---------------------------------

    if "format" in missing_components:

        instructions.append(
            "Choose a clear format that best fits "
            "the response."
        )

    # ---------------------------------
    # BUILD PROMPT
    # ---------------------------------

    enhanced_prompt = f"""
User Request:
{user_request}

Instructions:
"""

    # Add dynamic instructions.
    for instruction in instructions:

        enhanced_prompt += (
            f"\n- {instruction}"
        )

    # Always include this because it is
    # the core purpose of the enhancer.
    enhanced_prompt += """

Focus on accurately understanding the
user's intent and provide the most
helpful response possible.
"""

    return enhanced_prompt.strip()
