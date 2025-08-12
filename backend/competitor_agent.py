from __future__ import annotations

from typing import List, Dict, Any

from common import CLIENT, INDEX


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    resp = CLIENT.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding


def find_similar_competitors(description: str, top_k: int = 5) -> List[Dict[str, Any]]:
    query_vec = get_embedding(description)
    result = INDEX.query(vector=query_vec, top_k=top_k, include_metadata=True)
    matches = result.get("matches") if isinstance(result, dict) else getattr(result, "matches", [])
    return matches or []


def analyze_competitors(user_company_name: str, competitors: List[Dict[str, Any]]) -> str:
    system_msg = (
        "You are a precise and analytical SaaS market research assistant. "
        "Provide structured insights as requested."
    )
    prompt = (
        f"Analyze competitors of '{user_company_name}' on:\n"
        "- Danger Rating (1 minimal risk — 5 maximum threat)\n"
        "- Customer Experience (CX) strategy\n"
        "- Target audience\n"
        "- Donor portal UX (clunky, intuitive, etc.)\n"
        "- Messaging approach\n"
        "- Cross-selling of financial/charitable services\n"
        "- Availability of a mobile website or app\n"
    )
    context = "\n\n".join(
        f"{m['metadata'].get('name', m['id'])}: {m['metadata'].get('description', '')}"
        for m in competitors
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt + "\n\n" + context},
    ]

    resp = CLIENT.chat.completions.create(
        model="gpt-5",
        messages=messages,
        temperature=0.3,
        #verbosity="high",
        #reasoning_effort="medium",
    )
    return resp.choices[0].message.content
