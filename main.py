from validator import validate_request

from prompt_scorer import (
    score_prompt,
    get_missing_components
)

from prompt_enhancer import enhance_prompt

from database import (
    initialize_database,
    create_request,
    save_interaction,
    update_request
)


# =====================================
# EXIT COMMANDS
# =====================================

EXIT_COMMANDS = {
    "exit",
    "quit",
    "cancel",
    "never mind",
    "nevermind",
}


# =====================================
# GET USER REQUEST
# =====================================

def get_user_request():
    """Ask the user for their original request."""

    while True:

        user_request = input(
            "What would you like help with?\n> "
        ).strip()

        if not user_request:
            print(
                "\nPlease enter a request.\n"
            )
            continue

        # Exit commands only apply here,
        # when entering the original request.
        if is_exit_response(user_request):
            return None

        return user_request


# =====================================
# CHECK EXIT RESPONSE
# =====================================

def is_exit_response(answer):
    """
    Check whether the user explicitly wants
    to cancel the request.
    """

    return (
        answer.strip().lower()
        in EXIT_COMMANDS
    )


# =====================================
# UNDERSTANDING CLARIFICATIONS
# =====================================

def collect_understanding_clarifications(
    user_request,
    request_id
):
    """
    Ask clarification questions when the
    system cannot understand the user's
    request.

    Returns:
        final_request
        validation_result
    """

    current_request = user_request

    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:

        validation_result = validate_request(
            current_request
        )

        print(
            "\n--- Request Validation ---"
        )

        print(
            f"Understanding Score: "
            f"{validation_result['understanding_score']}/100"
        )

        # =============================
        # REQUEST IS UNDERSTOOD
        # =============================

        if not validation_result[
            "needs_clarification"
        ]:

            return (
                current_request,
                validation_result
            )

        # =============================
        # REQUEST NEEDS CLARIFICATION
        # =============================

        update_request(
            request_id=request_id,

            understanding_score=validation_result[
                "understanding_score"
            ],

            needs_clarification=True,

            status="needs_clarification"
        )

        print(
            "\nI need more information "
            "to understand your request."
        )

        print(
            "\nClarification Questions:"
        )

        questions = validation_result[
            "clarification_questions"
        ]

        for question in questions:

            # =========================
            # SAVE QUESTION
            # =========================

            save_interaction(
                request_id=request_id,

                interaction_type="understanding_question",

                content=question
            )

            answer = input(
                f"\n{question}\n> "
            ).strip()

            # =========================
            # USER CANCELS
            # =========================
            #
            # Only explicit cancellation
            # commands are accepted.
            #
            # "no" is a valid answer and
            # will NOT cancel the request.
            # =========================

            if is_exit_response(answer):

                save_interaction(
                    request_id=request_id,

                    interaction_type="cancellation",

                    content=answer
                )

                update_request(
                    request_id=request_id,

                    status="cancelled"
                )

                print(
                    "\nNo problem. "
                    "Request cancelled."
                )

                return None, None

            # =========================
            # EMPTY ANSWER
            # =========================

            if not answer:

                save_interaction(
                    request_id=request_id,

                    interaction_type="empty_answer",

                    content="[No answer provided]"
                )

                print(
                    "\nNo answer was provided."
                )

                continue

            # =========================
            # SAVE ANSWER
            # =========================

            save_interaction(
                request_id=request_id,

                interaction_type="understanding_answer",

                content=answer
            )

            current_request += (
                f"\nClarification: {answer}"
            )

        attempt += 1

        print(
            "\nThank you. "
            "Analyzing your updated request..."
        )

    # =============================
    # MAX ATTEMPTS REACHED
    # =============================

    update_request(
        request_id=request_id,

        status="failed_understanding"
    )

    print(
        "\nI still don't have enough "
        "information to understand "
        "your request."
    )

    return None, None


# =====================================
# MAIN PROGRAM
# =====================================

def main():

    # =================================
    # INITIALIZE DATABASE
    # =================================

    initialize_database()

    # =================================
    # GET USER REQUEST
    # =================================

    original_request = get_user_request()

    # User cancelled before creating
    # a database request.
    if original_request is None:

        print(
            "\nNo problem. Goodbye."
        )

        return

    # =================================
    # CREATE DATABASE REQUEST
    # =================================

    request_id = create_request(
        original_request
    )

    # =================================
    # SAVE ORIGINAL REQUEST
    # =================================

    save_interaction(
        request_id=request_id,

        interaction_type="user_request",

        content=original_request
    )

    # =================================
    # STEP 1
    # UNDERSTANDING VALIDATION
    # =================================

    final_request, validation_result = (
        collect_understanding_clarifications(
            original_request,
            request_id
        )
    )

    # =================================
    # STOP IF CANCELLED
    # =================================

    if final_request is None:
        return

    # =================================
    # STEP 2
    # SCORE ORIGINAL REQUEST
    # =================================

    original_scoring_result = (
        score_prompt(
            original_request
        )
    )

    print(
        "\n--- Original Prompt Score ---"
    )

    print(
        f"Total Score: "
        f"{original_scoring_result['total_score']}/100"
    )

    for category, score in (
        original_scoring_result[
            "scores"
        ].items()
    ):

        print(
            f"{category.capitalize()}: "
            f"{score}/20"
        )

    # =================================
    # STEP 3
    # SCORE FINAL REQUEST
    # =================================

    final_scoring_result = (
        score_prompt(
            final_request
        )
    )

    missing_components = (
        get_missing_components(
            final_scoring_result
        )
    )

    print(
        "\n--- Final Prompt Quality Analysis ---"
    )

    print(
        f"Prompt Score: "
        f"{final_scoring_result['total_score']}/100"
    )

    for category, score in (
        final_scoring_result[
            "scores"
        ].items()
    ):

        print(
            f"{category.capitalize()}: "
            f"{score}/20"
        )

    # =================================
    # SHOW MISSING COMPONENTS
    # =================================

    if missing_components:

        print(
            "\nMissing Components:"
        )

        for component in missing_components:

            print(
                f"- {component.capitalize()}"
            )

    else:

        print(
            "\nAll prompt components "
            "were detected."
        )

    # =================================
    # STEP 4
    # ENHANCE PROMPT
    # =================================

    enhanced_prompt = enhance_prompt(
        user_request=final_request,
        missing_components=missing_components
    )

    print(
        "\n--- Enhanced Prompt ---\n"
    )

    print(
        enhanced_prompt
    )

    # =================================
    # STEP 5
    # UPDATE DATABASE
    # =================================

    update_request(

        request_id=request_id,

        final_request=final_request,

        understanding_score=validation_result[
            "understanding_score"
        ],

        needs_clarification=False,

        prompt_score=final_scoring_result[
            "total_score"
        ],

        enhanced_prompt=enhanced_prompt,

        status="completed"
    )

    print(
        "\nRequest completed and saved "
        "successfully to the database."
    )


# =====================================
# PROGRAM ENTRY POINT
# =====================================

if __name__ == "__main__":
    main()
