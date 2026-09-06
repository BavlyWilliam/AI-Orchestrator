from request_analyzer import analyze_request

from prompt_enhancer import enhance_prompt

from prompt_scorer import (
    score_prompt,
    get_missing_components
)

from model_recommender import (
    recommend_models
)

from benchmark_provider import (
    fetch_benchmark_data
)

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

        # Exit commands only apply when
        # entering the original request.
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
# DISPLAY REQUEST ANALYSIS
# =====================================

def display_analysis(analysis_result):
    """
    Display the Gemini analysis in a
    readable format.
    """

    print(
        "\n--- Gemini Request Analysis ---"
    )

    print(
        f"Understanding Score: "
        f"{analysis_result.understanding_score}/100"
    )

    print(
        f"Task Category: "
        f"{analysis_result.task_category}"
    )

    print(
        f"Complexity: "
        f"{analysis_result.complexity}"
    )

    # =============================
    # MISSING COMPONENTS
    # =============================

    if analysis_result.missing_components:

        print(
            "\nMissing Components:"
        )

        for component in (
            analysis_result.missing_components
        ):

            print(
                f"- {component.capitalize()}"
            )

    else:

        print(
            "\nMissing Components: None"
        )

    # =============================
    # ANALYSIS REASON
    # =============================

    print(
        "\nAnalysis:"
    )

    print(
        analysis_result.analysis_reason
    )


# =====================================
# UNDERSTANDING CLARIFICATIONS
# =====================================

def collect_understanding_clarifications(
    user_request,
    request_id
):
    """
    Analyze the request using Gemini.

    If clarification is genuinely necessary,
    ask one focused clarification question.

    The updated request is then analyzed
    again.

    Returns:
        final_request
        analysis_result
    """

    current_request = user_request

    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:

        # =============================
        # ANALYZE REQUEST WITH GEMINI
        # =============================

        analysis_result = analyze_request(
            current_request
        )

        display_analysis(
            analysis_result
        )

        # =============================
        # SAVE ANALYSIS RESULTS
        # =============================

        update_request(
            request_id=request_id,

            understanding_score=(
                analysis_result.understanding_score
            ),

            needs_clarification=(
                analysis_result.needs_clarification
            ),

            task_category=(
                analysis_result.task_category
            )
        )

        # =============================
        # NON-ACTIONABLE REQUEST
        # =============================

        if not analysis_result.is_actionable_request:

            update_request(
                request_id=request_id,

                status="non_actionable"
            )

            print(
                "\nI couldn't find an actionable "
                "request to process."
            )

            return None, None

        # =============================
        # REQUEST IS READY
        # =============================

        if not analysis_result.needs_clarification:

            return (
                current_request,
                analysis_result
            )

        # =============================
        # CLARIFICATION REQUIRED
        # =============================

        question = (
            analysis_result.clarification_question
        )

        # Safety check in case Gemini says
        # clarification is needed but does
        # not provide a question.
        if not question:

            update_request(
                request_id=request_id,

                status="analysis_error"
            )

            print(
                "\nThe analyzer indicated that "
                "clarification is needed but did "
                "not provide a question."
            )

            return None, None

        # =============================
        # UPDATE DATABASE STATUS
        # =============================

        update_request(
            request_id=request_id,

            status="needs_clarification"
        )

        print(
            "\nClarification Needed:"
        )

        print(
            f"\n{question}"
        )

        # =============================
        # SAVE QUESTION
        # =============================

        save_interaction(
            request_id=request_id,

            interaction_type=(
                "clarification_question"
            ),

            content=question
        )

        # =============================
        # GET USER ANSWER
        # =============================

        answer = input(
            "\n> "
        ).strip()

        # =============================
        # USER CANCELS
        # =============================

        # "no" is NOT an exit command.
        # It is treated as a valid answer.

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

        # =============================
        # EMPTY ANSWER
        # =============================

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

        # =============================
        # SAVE ANSWER
        # =============================

        save_interaction(
            request_id=request_id,

            interaction_type=(
                "clarification_answer"
            ),

            content=answer
        )

        # =============================
        # ADD ANSWER TO REQUEST CONTEXT
        # =============================

        current_request += (
            f"\n\nClarification Question: "
            f"{question}"
        )

        current_request += (
            f"\nClarification Answer: "
            f"{answer}"
        )

        attempt += 1

        print(
            "\nThank you. "
            "Analyzing your updated request..."
        )

    # =================================
    # FINAL ANALYSIS AFTER MAX ATTEMPTS
    # =================================

    final_analysis = analyze_request(
        current_request
    )

    display_analysis(
        final_analysis
    )

    # =================================
    # STILL NEEDS CLARIFICATION
    # =================================

    if final_analysis.needs_clarification:

        update_request(
            request_id=request_id,

            understanding_score=(
                final_analysis.understanding_score
            ),

            needs_clarification=True,

            task_category=(
                final_analysis.task_category
            ),

            status="failed_understanding"
        )

        print(
            "\nI still need more information "
            "to process this request."
        )

        return None, None

    # =================================
    # FINAL REQUEST READY
    # =================================

    return (
        current_request,
        final_analysis
    )


# =====================================
# DISPLAY PROMPT SCORE
# =====================================

def display_prompt_score(scoring_result):
    """
    Display the enhanced prompt's component
    score in a readable format.
    """

    print(
        "\n--- Prompt Quality Score ---\n"
    )

    print(
        f"Total Score: "
        f"{scoring_result['total_score']}/100"
    )

    missing_components = get_missing_components(
        scoring_result
    )

    if missing_components:

        print(
            "\nComponents Not Detected:"
        )

        for component in missing_components:

            print(
                f"- {component.capitalize()}"
            )

    else:

        print(
            "\nAll components detected."
        )


# =====================================
# DISPLAY RECOMMENDATIONS
# =====================================

def display_recommendations(
    recommendation_result,
    used_benchmark_data
):
    """
    Display the AI model recommendation
    results in a readable format.
    """

    print(
        "\n--- AI Recommendations ---"
    )

    print(
        "\nRequest Analysis:"
    )

    analysis = recommendation_result[
        "request_analysis"
    ]

    print(
        f"Primary Task: "
        f"{analysis['primary_task']}"
    )

    print(
        f"Complexity: "
        f"{analysis['complexity']}"
    )

    print(
        "\nRecommendations:"
    )

    for recommendation in (
        recommendation_result[
            "recommendations"
        ]
    ):

        print(
            f"\n{recommendation['name']}"
        )

        print(
            f"Compatibility: "
            f"{recommendation['compatibility_score']}/100"
        )

        print(
            f"Reason: "
            f"{recommendation['reason']}"
        )

    best = recommendation_result[
        "best_recommendation"
    ]

    print(
        "\n--- Best Recommendation ---"
    )

    print(
        f"{best['name']} "
        f"({best['compatibility_score']}/100)"
    )

    print(
        best["reason"]
    )

    if used_benchmark_data:

        print(
            "\n(Benchmark data via Artificial Analysis "
            "— https://artificialanalysis.ai/)"
        )

    return best


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

    # =================================
    # USER CANCELLED
    # =================================

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
    # GEMINI REQUEST ANALYSIS
    # =================================

    try:

        final_request, analysis_result = (
            collect_understanding_clarifications(
                original_request,
                request_id
            )
        )

    except Exception as error:

        update_request(
            request_id=request_id,

            status="error"
        )

        print(
            "\nAn error occurred while "
            "analyzing the request:"
        )

        print(
            error
        )

        return

    # =================================
    # STOP IF REQUEST WAS NOT COMPLETED
    # =================================

    if final_request is None:

        return

    # =================================
    # STEP 2
    # ENHANCE PROMPT
    # =================================

    try:

        enhanced_prompt = enhance_prompt(
            final_request,
            analysis_result
        )

    except Exception as error:

        update_request(
            request_id=request_id,

            status="error"
        )

        print(
            "\nAn error occurred while "
            "enhancing the prompt:"
        )

        print(
            error
        )

        return

    print(
        "\n--- Enhanced Prompt ---\n"
    )

    print(
        enhanced_prompt
    )

    # =================================
    # STEP 3
    # SAVE ANALYSIS + ENHANCEMENT
    # =================================

    update_request(

        request_id=request_id,

        final_request=final_request,

        understanding_score=(
            analysis_result.understanding_score
        ),

        needs_clarification=(
            analysis_result.needs_clarification
        ),

        task_category=(
            analysis_result.task_category
        ),

        enhanced_prompt=enhanced_prompt,

        status="enhanced"
    )

    # =================================
    # STEP 4
    # SCORE THE ENHANCED PROMPT
    # =================================

    scoring_result = score_prompt(
        enhanced_prompt
    )

    update_request(
        request_id=request_id,

        prompt_score=(
            scoring_result["total_score"]
        )
    )

    display_prompt_score(
        scoring_result
    )

    # =================================
    # STEP 5
    # AI MODEL RECOMMENDATION
    # =================================

    try:

        benchmark_data = fetch_benchmark_data()

        recommendation_result = (
            recommend_models(
                final_request,
                benchmark_data
            )
        )

    except Exception as error:

        update_request(
            request_id=request_id,

            status="error"
        )

        print(
            "\nAn error occurred while "
            "generating AI model recommendations:"
        )

        print(
            error
        )

        return

    best = display_recommendations(
        recommendation_result,
        benchmark_data
    )

    # =================================
    # SAVE RECOMMENDATION + COMPLETE
    # =================================

    update_request(
        request_id=request_id,

        recommended_llm=best["name"],

        recommendation_reason=best["reason"],

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
