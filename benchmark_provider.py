import os

import requests

from dotenv import load_dotenv


# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()


# =====================================
# CONFIGURATION
# =====================================
#
# Wires up ARTIFICIAL_ANALYSIS_API_KEY (previously loaded but
# never used) to fetch live model benchmarks from Artificial
# Analysis, so model_recommender.py has real intelligence /
# coding / math / pricing data to reason about instead of
# always receiving an empty benchmark_data dict.
#
# Attribution: benchmark data is provided by Artificial
# Analysis (https://artificialanalysis.ai/). Per their API
# terms, any use of this data must be attributed back to them.

ARTIFICIAL_ANALYSIS_MODELS_URL = (
    "https://artificialanalysis.ai/api/v2/data/llms/models"
)

REQUEST_TIMEOUT_SECONDS = 10


# =====================================
# MODEL MATCHING
# =====================================
#
# Maps each supported option to the keywords used to find its
# closest current match in the Artificial Analysis dataset.
# All keywords for an option must appear (in the model's name,
# slug, or creator) for it to count as a match.
#
# Microsoft Copilot is intentionally excluded: it's a product
# wrapping other providers' models, not a benchmarked model in
# its own right, matching the "don't compare Copilot directly
# to model benchmarks" principle already in RECOMMENDATION_RULES.
#
# ChatGPT is matched to OpenAI's current flagship model, since
# target users can't manually pick a specific OpenAI model.

MODEL_MATCH_KEYWORDS = {
    "ChatGPT": ["openai"],
    "Claude Sonnet": ["claude", "sonnet"],
    "Claude Opus": ["claude", "opus"],
    "Gemini Flash": ["gemini", "flash"],
    "Gemini Pro": ["gemini", "pro"],
}


def _matches_all_keywords(haystack, keywords):
    """Check whether every keyword appears somewhere in haystack."""

    haystack_lower = haystack.lower()

    return all(
        keyword in haystack_lower
        for keyword in keywords
    )


def _best_match(models, keywords):
    """
    Return the highest-intelligence model whose name, slug, or
    creator matches every keyword. Returns None if nothing matches.
    """

    candidates = []

    for model in models:

        haystack = " ".join([
            model.get("name") or "",
            model.get("slug") or "",
            (model.get("model_creator") or {}).get("name") or ""
        ])

        if _matches_all_keywords(haystack, keywords):

            candidates.append(model)

    if not candidates:

        return None

    def intelligence_score(model):

        return (
            (model.get("evaluations") or {}).get(
                "artificial_analysis_intelligence_index"
            )
            or 0
        )

    candidates.sort(
        key=intelligence_score,
        reverse=True
    )

    return candidates[0]


def _summarize(model):
    """Pull out just the fields the recommender actually needs."""

    evaluations = model.get("evaluations") or {}
    pricing = model.get("pricing") or {}

    return {
        "matched_model_name": model.get("name"),
        "intelligence_index": evaluations.get(
            "artificial_analysis_intelligence_index"
        ),
        "coding_index": evaluations.get(
            "artificial_analysis_coding_index"
        ),
        "math_index": evaluations.get(
            "artificial_analysis_math_index"
        ),
        "price_per_1m_blended_tokens": pricing.get(
            "price_1m_blended_3_to_1"
        ),
        "output_tokens_per_second": model.get(
            "median_output_tokens_per_second"
        )
    }


# =====================================
# FETCH BENCHMARK DATA
# =====================================

def fetch_benchmark_data():
    """
    Fetch current LLM benchmarks from Artificial Analysis and
    return a dict keyed by supported option name.

    Returns None if the API key is missing or the request fails
    for any reason, rather than raising - a benchmark outage
    should never block a recommendation, it should just fall
    back to reasoning without benchmark numbers.
    """

    api_key = os.getenv("ARTIFICIAL_ANALYSIS_API_KEY")

    if not api_key:

        return None

    try:

        response = requests.get(
            ARTIFICIAL_ANALYSIS_MODELS_URL,
            headers={"x-api-key": api_key},
            timeout=REQUEST_TIMEOUT_SECONDS
        )

        response.raise_for_status()

        models = response.json().get("data", [])

    except (requests.RequestException, ValueError):

        return None

    benchmark_data = {}

    for option_name, keywords in MODEL_MATCH_KEYWORDS.items():

        match = _best_match(models, keywords)

        if match:

            benchmark_data[option_name] = _summarize(match)

    if not benchmark_data:

        return None

    benchmark_data["_attribution"] = (
        "https://artificialanalysis.ai/"
    )

    return benchmark_data
