import json
import os

from dotenv import load_dotenv
from google import genai


# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()


# =====================================
# SUPPORTED AI PRODUCTS
# =====================================

SUPPORTED_OPTIONS = [
    {
        "name": "ChatGPT",
        "type": "ai_assistant",
        "provider": "OpenAI",
        "notes": (
            "Recommend ChatGPT as a product, not a specific "
            "OpenAI model. The target users are primarily "
            "Free and Go tier users who cannot freely select "
            "specific models."
        )
    },
    {
        "name": "Claude Sonnet",
        "type": "model",
        "provider": "Anthropic",
        "notes": (
            "General-purpose Claude option. Consider for "
            "coding, writing, analysis, and complex tasks."
        )
    },
    {
        "name": "Claude Opus",
        "type": "model",
        "provider": "Anthropic",
        "notes": (
            "Premium Claude option. Consider when the task "
            "requires unusually deep reasoning or complexity."
        )
    },
    {
        "name": "Gemini Flash",
        "type": "model",
        "provider": "Google",
        "notes": (
            "General-purpose Gemini option."
        )
    },
    {
        "name": "Gemini Pro",
        "type": "model",
        "provider": "Google",
        "notes": (
            "Advanced Gemini option for complex reasoning, "
            "coding, mathematics, and multimodal tasks."
        )
    },
    {
        "name": "Microsoft Copilot",
        "type": "ai_assistant",
        "provider": "Microsoft",
        "notes": (
            "Give special consideration when the request "
            "involves Microsoft products or workflows such as "
            "Excel, Word, PowerPoint, Outlook, Teams, Windows, "
            "or other Microsoft ecosystem tasks."
        )
    }
]


# =====================================
# RECOMMENDATION RULES
# =====================================

RECOMMENDATION_RULES = """
You are an AI model and AI assistant recommendation engine.

Your job is to analyze a user's request semantically and
determine which AI option is most compatible with that request.

Do NOT use simple keyword matching.

You must understand the actual meaning, requirements,
complexity, and context of the user's request.

You are recommending from ONLY these options:

- ChatGPT
- Claude Sonnet
- Claude Opus
- Gemini Flash
- Gemini Pro
- Microsoft Copilot


IMPORTANT RECOMMENDATION PRINCIPLES:

1. Do not automatically recommend the most powerful model.

The best option depends on what the user actually needs.

A simple task does not automatically require the most powerful
model.

2. Consider the actual task requirements.

Examples may include:

- Coding
- Debugging
- Complex reasoning
- Research
- Writing
- Data analysis
- Learning
- Mathematics
- Image analysis
- Document analysis
- Creative work
- Planning
- Microsoft ecosystem integration

3. Microsoft Copilot is a special case.

Give Microsoft Copilot strong consideration when the user's
request primarily involves Microsoft products or workflows.

Examples:

- Excel
- Word
- PowerPoint
- Outlook
- Teams
- Windows
- Microsoft 365

Copilot may also receive consideration when practical product
advantages make it more useful than raw model intelligence.

Do not treat Copilot as if it were directly comparable to
benchmark scores for underlying language models.

4. ChatGPT is a product recommendation.

The target audience includes ChatGPT Free and Go users.

Do not assume that these users can manually choose between
specific OpenAI models.

Recommend "ChatGPT" as the user-facing product.

5. Benchmark information matters.

When benchmark data is provided, consider it as evidence.

Use benchmark data that is relevant to the request.

For example:

- Coding benchmarks matter more for coding tasks.
- Intelligence and reasoning benchmarks matter more for
  complex reasoning tasks.

Do not use benchmark scores blindly.

A higher benchmark score does not automatically mean that an
option is the best choice.

6. Product fit matters.

A slightly less capable model may be a better recommendation
when the user's workflow strongly benefits from a particular
AI product or ecosystem.

7. Individual users are the target audience.

Do NOT prioritize:

- API pricing
- Enterprise cost optimization
- Token pricing

Speed is also NOT a major recommendation factor unless the
user explicitly says they need a fast response.

8. Compatibility scores must represent task fit.

Give every supported option a compatibility score from 0 to 100.

The scores should be relative to the user's request.

Use the full range when appropriate.

Do not give every option similar scores.

9. Explain the recommendation clearly.

The explanation should describe WHY the top option matches
the user's request.

Do not claim capabilities that you cannot justify.

10. Be honest.

If multiple options are similarly appropriate, reflect that
in the scores and explanation.
"""


# =====================================
# GEMINI CLIENT
# =====================================

def get_client():
    """
    Create a Gemini client using the API key
    stored in the .env file.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Check your .env file."
        )

    return genai.Client(
        api_key=api_key
    )


# =====================================
# GEMINI ANALYSIS
# =====================================

def recommend_models(
    user_request,
    benchmark_data=None
):
    """
    Analyze the user's request using Gemini and return
    compatibility scores for supported AI options.

    benchmark_data can contain benchmark information from
    Artificial Analysis (see benchmark_provider.py).
    """

    client = get_client()

    prompt = f"""
{RECOMMENDATION_RULES}


SUPPORTED OPTIONS:

{json.dumps(SUPPORTED_OPTIONS, indent=2)}


BENCHMARK DATA:

{json.dumps(benchmark_data or {}, indent=2)}


USER REQUEST:

{user_request}


Return ONLY valid JSON.

Use this exact structure:

{{
    "request_analysis": {{
        "primary_task": "string",
        "complexity": "simple | medium | complex",
        "reasoning_required": "low | medium | high",
        "coding_required": "low | medium | high",
        "microsoft_ecosystem_relevance":
            "low | medium | high",
        "important_requirements": [
            "requirement"
        ]
    }},
    "recommendations": [
        {{
            "name": "Supported option name",
            "compatibility_score": 0,
            "reason": "Short explanation"
        }}
    ],
    "best_recommendation": {{
        "name": "Supported option name",
        "compatibility_score": 0,
        "reason": "Clear explanation"
    }}
}}

Rules for the JSON:

- Include ALL supported options.
- compatibility_score must be an integer from 0 to 100.
- Sort recommendations from highest score to lowest score.
- The first recommendation should normally match
  best_recommendation.
- Do not invent additional AI models.
- Return valid JSON only.
"""

    # Uses the same Interactions API convention as
    # request_analyzer.py and prompt_enhancer.py, instead of
    # the older client.models.generate_content() call this
    # function used previously - keeps one consistent way of
    # talking to Gemini across the whole project.
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json"
        }
    )

    if not interaction.output_text:
        raise RuntimeError(
            "Gemini returned an empty recommendation response."
        )

    return parse_recommendation_response(
        interaction.output_text.strip()
    )


# =====================================
# PARSE GEMINI RESPONSE
# =====================================

def parse_recommendation_response(
    response_text
):
    """
    Convert Gemini's JSON response into a Python dictionary.
    """

    try:

        result = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        raise ValueError(
            "Gemini returned invalid JSON."
        )

    validate_recommendation_result(
        result
    )

    return result


# =====================================
# VALIDATE RESULT
# =====================================

def validate_recommendation_result(
    result
):
    """
    Validate Gemini's response before the program
    uses the recommendation.
    """

    if not isinstance(result, dict):

        raise ValueError(
            "Recommendation result must be a dictionary."
        )

    required_keys = [
        "request_analysis",
        "recommendations",
        "best_recommendation"
    ]

    for key in required_keys:

        if key not in result:

            raise ValueError(
                f"Missing required key: {key}"
            )

    recommendations = result[
        "recommendations"
    ]

    if not isinstance(
        recommendations,
        list
    ):

        raise ValueError(
            "Recommendations must be a list."
        )

    supported_names = {
        option["name"]
        for option in SUPPORTED_OPTIONS
    }

    returned_names = {
        recommendation["name"]
        for recommendation in recommendations
    }

    if returned_names != supported_names:

        raise ValueError(
            "Gemini did not return exactly the "
            "supported AI options."
        )

    for recommendation in recommendations:

        score = recommendation.get(
            "compatibility_score"
        )

        if (
            not isinstance(score, int)
            or score < 0
            or score > 100
        ):

            raise ValueError(
                "Compatibility scores must be "
                "integers between 0 and 100."
            )

    scores = [
        recommendation["compatibility_score"]
        for recommendation in recommendations
    ]

    if scores != sorted(
        scores,
        reverse=True
    ):

        raise ValueError(
            "Recommendations are not sorted "
            "from highest to lowest score."
        )

    best = result[
        "best_recommendation"
    ]

    if best["name"] not in supported_names:

        raise ValueError(
            "Best recommendation is not supported."
        )
