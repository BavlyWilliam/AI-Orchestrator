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
    # BASIC INTENTION
    # ---------------------------------

    understanding_score += 30

    # ---------------------------------
    # IDENTIFY ACTION
    # ---------------------------------

    action_keywords = [
        "create",
        "build",
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
        "plan"
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
    # IDENTIFY A SUBJECT / OBJECT
    # ---------------------------------

    words = request.split()

    if len(words) >= 3:

        understanding_score += 20

    else:

        clarification_questions.append(
            "What specifically would you like help with?"
        )

    # ---------------------------------
    # TASK-SPECIFIC CLARIFICATION
    # ---------------------------------

    # CREATE / BUILD TASKS

    creation_keywords = [
        "create",
        "build",
        "make",
        "design"
    ]

    if any(keyword in request for keyword in creation_keywords):

        understanding_score += 20

        vague_creation_objects = [
            "tracker",
            "app",
            "application",
            "website",
            "program",
            "system",
            "dashboard"
        ]

        for item in vague_creation_objects:

            if item in request:

                clarification_questions.append(
                    f"What should the {item} specifically do?"
                )

                break

    # RECOMMENDATION TASKS

    elif "recommend" in request or "best" in request:

        understanding_score += 20

        clarification_questions.append(
            "What will you primarily use it for?"
        )

    # EXPLANATION TASKS

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
    # DECISION
    # ---------------------------------

    needs_clarification = (
        len(clarification_questions) > 0
    )

    return {
        "understanding_score": understanding_score,
        "needs_clarification": needs_clarification,
        "clarification_questions": clarification_questions
    }
