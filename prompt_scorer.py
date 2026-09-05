def score_prompt(prompt):
    """
    Score a prompt based on five components:

    Context
    Role
    Task
    Output
    Format
    """

    request = prompt.lower().strip()

    scores = {
        "context": 0,
        "role": 0,
        "task": 0,
        "output": 0,
        "format": 0
    }

    # ---------------------------------
    # CONTEXT
    # ---------------------------------

    context_keywords = [
        "i am",
        "i'm",
        "my",
        "because",
        "currently",
        "working on",
        "beginner",
        "advanced",
        "experience",
        "project"
    ]

    if any(keyword in request for keyword in context_keywords):

        scores["context"] = 20

    # ---------------------------------
    # ROLE
    # ---------------------------------

    role_keywords = [
        "you are",
        "act as",
        "behave as",
        "expert",
        "specialist",
        "teacher",
        "developer",
        "engineer",
        "consultant"
    ]

    if any(keyword in request for keyword in role_keywords):

        scores["role"] = 20

    # ---------------------------------
    # TASK
    # ---------------------------------

    task_keywords = [
        "create",
        "build",
        "write",
        "explain",
        "teach",
        "analyze",
        "recommend",
        "compare",
        "debug",
        "fix",
        "design",
        "summarize",
        "plan"
    ]

    if any(keyword in request for keyword in task_keywords):

        scores["task"] = 20

    # ---------------------------------
    # OUTPUT
    # ---------------------------------

    output_keywords = [
        "include",
        "provide",
        "give me",
        "show me",
        "generate",
        "return",
        "examples",
        "steps",
        "solution"
    ]

    if any(keyword in request for keyword in output_keywords):

        scores["output"] = 20

    # ---------------------------------
    # FORMAT
    # ---------------------------------

    format_keywords = [
        "bullet points",
        "table",
        "json",
        "list",
        "step-by-step",
        "sections",
        "markdown",
        "format"
    ]

    if any(keyword in request for keyword in format_keywords):

        scores["format"] = 20

    # ---------------------------------
    # TOTAL SCORE
    # ---------------------------------

    total_score = sum(scores.values())

    return {
        "total_score": total_score,
        "scores": scores
    }
