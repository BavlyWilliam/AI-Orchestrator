from validator import validate_request
from prompt_scorer import score_prompt
from prompt_enhancer import enhance_prompt
from database import initialize_database, save_request


EXIT_COMMANDS = {
    "exit",
    "quit",
    "cancel",
    "stop",
    "no",
    "nothing",
    "never mind",
    "nevermind",
    "leave me alone",
    "fuck off"
}


def get_user_request():
    """Ask the user for their original request."""

    while True:

        user_request = input(
            "What would you like help with?\n> "
        ).strip()

        if user_request:
            return user_request

        print("\nPlease enter a request.\n")


def is_exit_response(answer):
    """
    Check whether the user wants to stop
    the clarification process.
    """

    return answer.strip().lower() in EXIT_COMMANDS


def collect_clarifications(user_request):
    """
    Ask clarification questions until:

    - The request is clear enough
    - The user cancels
    - The maximum number of attempts is reached
    """

    current_request = user_request

    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:

        validation_result = validate_request(
            current_request
        )

        print("\n--- Request Validation ---")

        print(
            f"Understanding Score: "
            f"{validation_result['understanding_score']}/100"
        )

        # ---------------------------------
        # REQUEST IS CLEAR
        # ---------------------------------

        if not validation_result[
            "needs_clarification"
        ]:

            return current_request, validation_result

        # ---------------------------------
        # REQUEST NEEDS CLARIFICATION
        # ---------------------------------

        print(
            "\nYour request needs clarification."
        )

        print("\nClarification Questions:")

        for question in validation_result[
            "clarification_questions"
        ]:

            answer = input(
                f"\n{question}\n> "
            ).strip()

            # ---------------------------------
            # USER CANCELS
            # ---------------------------------

            if is_exit_response(answer):

                print(
                    "\nNo problem. Request cancelled."
                )

                return None, None

            # ---------------------------------
            # EMPTY ANSWER
            # ---------------------------------

            if not answer:

                print(
                    "\nNo answer was provided."
                )

                continue

            # ---------------------------------
            # ADD CLARIFICATION
            # ---------------------------------

            current_request += (
                f"\nClarification: {answer}"
            )

        attempt += 1

        print(
            "\nThank you. "
            "Analyzing your updated request..."
        )

    # ---------------------------------
    # MAXIMUM ATTEMPTS REACHED
    # ---------------------------------

    print(
        "\nI still don't have enough information "
        "to understand your request."
    )

    print(
        "Please start again with a clearer request."
    )

    return None, None


def main():

    # ---------------------------------
    # INITIALIZE DATABASE
    # ---------------------------------

    initialize_database()

    # ---------------------------------
    # GET ORIGINAL REQUEST
    # ---------------------------------

    original_request = get_user_request()

    # ---------------------------------
    # COLLECT CLARIFICATIONS
    # ---------------------------------

    final_request, validation_result = (
        collect_clarifications(
            original_request
        )
    )

    # ---------------------------------
    # STOP IF REQUEST WAS CANCELLED
    # ---------------------------------

    if final_request is None:

        return

    # ---------------------------------
    # SCORE ORIGINAL PROMPT
    # ---------------------------------

    scoring_result = score_prompt(
        original_request
    )

    print("\n--- Original Prompt Score ---")

    print(
        f"Total Score: "
        f"{scoring_result['total_score']}/100"
    )

    for category, score in scoring_result[
        "scores"
    ].items():

        print(
            f"{category.capitalize()}: "
            f"{score}/20"
        )

    # ---------------------------------
    # ENHANCE PROMPT
    # ---------------------------------

    enhanced_prompt = enhance_prompt(
        final_request
    )

    print("\n--- Enhanced Prompt ---\n")

    print(enhanced_prompt)

    # ---------------------------------
    # SAVE REQUEST
    # ---------------------------------

    save_request(
        original_prompt=original_request,
        understanding_score=validation_result[
            "understanding_score"
        ],
        needs_clarification=False,
        prompt_score=scoring_result[
            "total_score"
        ],
        enhanced_prompt=enhanced_prompt
    )

    print(
        "\nRequest saved successfully "
        "to the database."
    )


if __name__ == "__main__":
    main()
