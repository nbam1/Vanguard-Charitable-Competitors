from __future__ import annotations

import os
from typing import List, Dict, Any

import openai
import pinecone
from dotenv import load_dotenv

load_dotenv()

CLIENT = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PC = pinecone.Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV"),
)
INDEX_NAME = os.getenv("PINECONE_INDEX", "index2")
INDEX = PC.Index(INDEX_NAME)


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    resp = CLIENT.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding


def find_similar_competitors(description: str, top_k: int = 5) -> List[Dict[str, Any]]:
    query_vec = get_embedding(description)
    result = INDEX.query(vector=query_vec, top_k=top_k, include_metadata=True)
    # SDK may return dict-like; normalize
    matches = result.get("matches") if isinstance(result, dict) else getattr(result, "matches", [])
    return matches or []


def analyze_competitors(user_company_name: str, competitors: List[Dict[str, Any]]) -> str:
    prompt = (
        f"You are a SaaS market analyst. Analyze the following competitors of "
        f"'{user_company_name}' and for each one, provide:\n"
        "- Danger Rating (1 = not dangerous, 5 = very dangerous)\n"
        "- CX strategy\n"
        "- Target audience\n"
        "- Donor portal UX (e.g., clunky, intuitive)\n"
        "- Messaging\n"
        "- Cross-selling of financial or charitable services\n"
        "- Whether they offer a mobile website or app\n"
    )

    lines = [
        f"{m['metadata'].get('name', m.get('id'))}: {m['metadata'].get('description', '')}"
        for m in competitors
    ]
    context = "\n\n".join(lines)

    messages = [
        {"role": "system", "content": "You are a helpful competitor analysis agent."},
        {"role": "user", "content": prompt + "\n\n" + context},
    ]

    resp = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content
