from __future__ import annotations

from typing import Any, Dict, List

from common import CLIENT, INDEX
from utils import fetch_company_info


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    resp = CLIENT.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding


def find_similar_competitors(description: str, top_k: int = 15) -> List[Dict[str, Any]]:
    query_vec = get_embedding(description)
    result = INDEX.query(vector=query_vec, top_k=top_k, include_metadata=True)
    matches = result.get("matches") if isinstance(result, dict) else getattr(result, "matches", [])
    return matches or []


def analyze_competitors(
    user_company_name: str, competitors: List[Dict[str, any]]
) -> str:
    """
    Generate a professional, detailed analysis of competitors.

    This function uses scraped website data as the primary source. If the
    scraped content is insufficient, it supplements it with data from
    Wikipedia or news sources.

    Args:
        user_company_name: The name of the company requesting the analysis.
        competitors: A list of competitor match dictionaries containing
                     'metadata' with 'name' and 'description'.

    Returns:
        A formatted string with competitor analyses.
    """
    enriched_contexts: List[str] = []

    for match in competitors:
        name = match["metadata"].get("name", match.get("id"))
        description = match["metadata"].get("description", "").strip()

        if not description or len(description.split()) < 80:
            extra_info = fetch_company_info(name)
            if extra_info:
                description = (
                    f"{description}\n\n"
                    f"Additional context from external sources:\n{extra_info}"
                )

        enriched_contexts.append(f"{name}: {description}")

    context = "\n\n".join(enriched_contexts)

    system_msg = (
        "You are a precise and analytical SaaS market research assistant. "
        "First, rely on the provided scraped and stored data to produce the "
        "analysis. If the provided data is insufficient to form a complete, "
        "professional report, integrate relevant facts from the additional "
        "context section."
    )

    prompt = (
        f"Analyze competitors of '{user_company_name}' in detail.\n"
        "- Danger Rating (1 minimal risk — 5 maximum threat, with justification)\n"
        "- Customer Experience (CX) strategy\n"
        "- Target audience\n"
        "- Donor portal UX (clunky, intuitive, etc.)\n"
        "- Messaging approach\n"
        "- Cross-selling of financial/charitable services\n"
        "- Availability of a mobile website or app\n"
        "Your tone should be professional and consultative, with enough detail "
        "to inform strategic decisions."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"{prompt}\n\n{context}"},
    ]

    resp = CLIENT.chat.completions.create(
        model="gpt-5",
        messages=messages,
    )
    return resp.choices[0].message.content
