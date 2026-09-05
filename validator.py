import re


def contains_keyword(text, keyword):
    """
    Check for a keyword or phrase using
    word boundaries.

    This prevents:
    - "fix" matching "fixture"
    - "make" matching "makeup"
    """

    pattern = (
        r"\b"
        + re.escape(keyword)
        + r"\b"
    )

    return (
        re.search(
            pattern,
            text
        )
        is not None
    )


def validate_request(user_request):
    """
    Determine whether the user's request is
    understandable enough to proceed.

    Returns:
        understanding_score
        needs_clarification
        clarification_questions
    """

    request = user_request.strip().lower()

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
    # DETECT PREVIOUS CLARIFICATIONS
    # ---------------------------------

    has_clarification = (
        "clarification:" in request
    )

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
        contains_keyword(
            request,
            keyword
        )
        for keyword in action_keywords
    )

    # ---------------------------------
    # WORD COUNT
    # ---------------------------------

    word_count = len(
        request.split()
    )

    # ---------------------------------
    # REQUEST TYPE DETECTION
    # ---------------------------------

    creation_keywords = [
        "create",
        "build",
        "make",
        "design"
    ]

    purchase_keywords = [
        "buy",
        "buying",
        "purchase",
        "purchasing"
    ]

    recommendation_keywords = [
        "recommend"
    ]

    explanation_keywords = [
        "explain",
        "teach"
    ]

    is_creation_request = any(
        contains_keyword(
            request,
            keyword
        )
        for keyword in creation_keywords
    )

    is_purchase_request = any(
        contains_keyword(
            request,
            keyword
        )
        for keyword in purchase_keywords
    )

    is_recommendation_request = any(
        contains_keyword(
            request,
            keyword
        )
        for keyword in recommendation_keywords
    )

    is_explanation_request = any(
        contains_keyword(
            request,
            keyword
        )
        for keyword in explanation_keywords
    )

    # ---------------------------------
    # VAGUE CREATION OBJECTS
    # ---------------------------------

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

    has_vague_creation_object = any(
        contains_keyword(
            request,
            item
        )
        for item in vague_creation_objects
    )

    # ---------------------------------
    # IDENTIFY CLARIFICATION NEEDS
    # ---------------------------------

    if not has_action:

        clarification_questions.append(
            "What would you like me to help you do?"
        )

    if word_count < 3:

        clarification_questions.append(
            "What specifically would you like help with?"
        )

    if (
        is_creation_request
        and has_vague_creation_object
        and not has_clarification
    ):

        clarification_questions.append(
            "What should it specifically do or be used for?"
        )

    if (
        is_purchase_request
        and not has_clarification
    ):

        clarification_questions.append(
            "What will you primarily use it for?"
        )

    if (
        is_recommendation_request
        and not has_clarification
    ):

        clarification_questions.append(
            "What will you primarily use it for?"
        )

    # ---------------------------------
    # CALCULATE UNDERSTANDING SCORE
    # ---------------------------------

    understanding_score = 0

    # A meaningful request exists.
    understanding_score += 30

    # System understands what the user
    # generally wants to do.
    if has_action:

        understanding_score += 30

    # The request contains enough detail
    # beyond just one or two words.
    if word_count >= 3:

        understanding_score += 20

    # No clarification is currently needed.
    if not clarification_questions:

        understanding_score += 20

    # ---------------------------------
    # FINAL SCORE
    # ---------------------------------

    understanding_score = min(
        understanding_score,
        100
    )

    needs_clarification = (
        len(clarification_questions) > 0
    )

    return {
        "understanding_score": understanding_score,

        "needs_clarification": (
            needs_clarification
        ),

        "clarification_questions": (
            clarification_questions
        )
    }
