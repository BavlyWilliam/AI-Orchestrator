import re


CONTEXT_KEYWORDS = [
    "context",
    "background",
    "because",
    "i am",
    "i'm",
    "my company",
    "my business",
    "my project",
    "given that",
    "considering",
    "based on",
    "working on"
]


ROLE_KEYWORDS = [
    "you are",
    "act as",
    "behave as",
    "role",
    "pretend to be",
    "imagine you are",
    "you're a",
    "acting as"
]


TASK_KEYWORDS = [
    "create",
    "build",
    "make",
    "write",
    "help",
    "explain",
    "analyze",
    "design",
    "develop",
    "debug",
    "recommend",
    "compare",
    "plan",
    "generate",
    "summarize",
    "translate",
    "fix",
    "optimize",
    "review"
]


OUTPUT_KEYWORDS = [
    "output",
    "result",
    "include",
    "provide",
    "give me",
    "return",
    "show me",
    "answer",
    "respond with",
    "deliver"
]


FORMAT_KEYWORDS = [
    "format",
    "bullet points",
    "table",
    "step by step",
    "steps",
    "json",
    "markdown",
    "list",
    "numbered list",
    "outline",
    "csv"
]


CATEGORY_KEYWORDS = {
    "context": CONTEXT_KEYWORDS,
    "role": ROLE_KEYWORDS,
    "task": TASK_KEYWORDS,
    "output": OUTPUT_KEYWORDS,
    "format": FORMAT_KEYWORDS,
}


# =====================================
# INFLECTION MATCHING
# =====================================

INFLECTION_KEYWORDS = {
    "debug",
    "recommend",
    "analyze",
    "develop",
    "optimize",
}


def _matches(text, keyword):
    """
    Check whether a keyword appears in text.

    Normal keywords require complete word
    boundaries.

    Selected verbs are allowed to match
    common inflected forms.

    Examples:

    "list"
    matches "list"
    does NOT match "listen"

    "fix"
    matches "fix"
    does NOT match "fixture"

    "debug"
    matches "debug"
    matches "debugging"
    """

    escaped = re.escape(keyword)

    # Multi-word phrases always require
    # complete boundaries.
    if " " in keyword:

        pattern = (
            r"\b"
            + escaped
            + r"\b"
        )

    # Allow selected verbs to match
    # inflected forms.
    elif keyword in INFLECTION_KEYWORDS:

        pattern = (
            r"\b"
            + escaped
        )

    # All other keywords must match
    # complete words.
    else:

        pattern = (
            r"\b"
            + escaped
            + r"\b"
        )

    return (
        re.search(
            pattern,
            text
        )
        is not None
    )


def score_prompt(prompt):
    """
    Score a prompt based on five main
    components:

    - Context
    - Role
    - Task
    - Output
    - Format
    """

    scores = {
        "context": 0,
        "role": 0,
        "task": 0,
        "output": 0,
        "format": 0
    }

    if (
        not isinstance(prompt, str)
        or not prompt.strip()
    ):

        return {
            "total_score": 0,
            "scores": scores
        }

    prompt_lower = prompt.lower()

    for category, keywords in (
        CATEGORY_KEYWORDS.items()
    ):

        if any(
            _matches(
                prompt_lower,
                keyword
            )
            for keyword in keywords
        ):

            scores[category] = 20

    total_score = sum(
        scores.values()
    )

    return {
        "total_score": total_score,
        "scores": scores
    }


def get_missing_components(scoring_result):
    """
    Return prompt components that
    received a score of zero.
    """

    return [
        component
        for component, score in (
            scoring_result[
                "scores"
            ].items()
        )
        if score == 0
    ]
