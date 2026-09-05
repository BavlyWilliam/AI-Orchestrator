def validate_request(user_request):
    """
    Determine whether the user's request is understandable
    enough to proceed with prompt enhancement.

    Returns:
        understanding_score
        needs_clarification
        clarification_questions
    """

    request = user_request.strip().lower()

    understanding_score = 0
    clarification_questions = []

    # ---------------------------------
    # EMPTY REQUEST
    # ---------------------------------

    if not request:

        return {
            "understanding_score": 0,
            "needs_clarification": True,
            "clarification_questions": [
                "What would you like help with?"
            ]
        }

    # ---------------------------------
    # BASIC REQUEST EXISTS
    # ---------------------------------

    understanding_score += 30

    # ---------------------------------
    # IDENTIFY USER INTENT
    # ---------------------------------

    action_keywords = [
        "create",
        "build",
        "make",
        "write",
        "explain",
        "teach",
        "help",
        "analyze",
        "recommend",
        "compare",
        "debug",
        "fix",
        "design",
        "summarize",
        "plan",
        "buy",
        "buying",
        "purchase",
        "purchasing"
    ]

    has_action = any(
        keyword in request
        for keyword in action_keywords
    )

    if has_action:

        understanding_score += 30

    else:

        clarification_questions.append(
            "What would you like me to help you do?"
        )

    # ---------------------------------
    # CHECK FOR SUBJECT / OBJECT
    # ---------------------------------

    word_count = len(request.split())

    if word_count >= 3:

        understanding_score += 20

    else:

        clarification_questions.append(
            "What specifically would you like help with?"
        )

    # ---------------------------------
    # CHECK FOR PREVIOUS CLARIFICATIONS
    # ---------------------------------

    has_clarification = (
        "clarification:" in request
    )

    # ---------------------------------
    # CREATION REQUESTS
    # ---------------------------------

    creation_keywords = [
        "create",
        "build",
        "make",
        "design"
    ]

    if any(
        keyword in request
        for keyword in creation_keywords
    ):

        understanding_score += 20

        if not has_clarification:

            vague_creation_objects = [
                "tracker",
                "app",
                "application",
                "website",
                "program",
                "system",
                "dashboard",
                "file"
            ]

            if any(
                item in request
                for item in vague_creation_objects
            ):

                clarification_questions.append(
                    "What should it specifically do or be used for?"
                )

    # ---------------------------------
    # PURCHASE REQUESTS
    # ---------------------------------

    elif any(
        keyword in request
        for keyword in [
            "buy",
            "buying",
            "purchase",
            "purchasing"
        ]
    ):

        understanding_score += 20

        if not has_clarification:

            clarification_questions.append(
                "What will you primarily use it for?"
            )

    # ---------------------------------
    # RECOMMENDATION REQUESTS
    # ---------------------------------

    elif (
        "recommend" in request
        or "best" in request
    ):

        understanding_score += 20

        if not has_clarification:

            clarification_questions.append(
                "What will you primarily use it for?"
            )

    # ---------------------------------
    # EXPLANATION REQUESTS
    # ---------------------------------

    elif (
        "explain" in request
        or "teach" in request
    ):

        understanding_score += 20

    # ---------------------------------
    # FINAL SCORE
    # ---------------------------------

    understanding_score = min(
        understanding_score,
        100
    )

    # ---------------------------------
    # FINAL DECISION
    # ---------------------------------

    needs_clarification = (
        len(clarification_questions) > 0
    )

    return {
        "understanding_score": understanding_score,
        "needs_clarification": needs_clarification,
        "clarification_questions": clarification_questions
    }
