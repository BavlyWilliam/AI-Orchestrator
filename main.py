from validator import validate_request
from prompt_scorer import score_prompt
from prompt_enhancer import enhance_prompt
from database import initialize_database, save_request


def get_user_request():
    """Ask the user for their original request."""

    while True:

        user_request = input(
            "What would you like help with?\n> "
        ).strip()

        if user_request:
            return user_request

        print("\nPlease enter a request.\n")


def collect_clarifications(user_request):
    """
    Ask clarification questions until the validator
    determines that the request is clear enough.
    """

    current_request = user_request

    while True:

        validation_result = validate_request(
            current_request
        )

        print("\n--- Request Validation ---")

        print(
            f"Understanding Score: "
            f"{validation_result['understanding_score']}/100"
        )

        # If no clarification is needed,
        # return the completed request.
        if not validation_result["needs_clarification"]:

            return current_request, validation_result

        print("\nYour request needs clarification.")

        print("\nClarification Questions:")

        # Ask every clarification question.
        for question in validation_result[
            "clarification_questions"
        ]:

            answer = input(
                f"\n{question}\n> "
            ).strip()

            # Add the user's clarification
            # to the existing request.
            if answer:

                current_request += (
                    f"\nClarification: {answer}"
                )

        print(
            "\nThank you. Analyzing your updated request..."
        )
