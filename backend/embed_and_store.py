from __future__ import annotations

from typing import Dict, Optional

import pinecone
import requests
from common import CLIENT
from scrape_website import scrape_website
from utils import fetch_company_info, vector_exists


def embed_text(text: str) -> list[float]:
    """Create an embedding with text-embedding-3-small (dim=1536)."""
    resp = CLIENT.embeddings.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return resp.data[0].embedding


def upsert_website(
    *,
    index: pinecone.Index,
    url: str,
    company_id: str,
    name: str,
    fallback_summary: str = "",
    extra_metadata: Optional[Dict[str, str]] = None,
) -> None:
    if vector_exists(index, company_id):
        print(f"Skip (exists): {url} -> {company_id}")
        return

    content = fallback_summary
    try:
        scraped = scrape_website(url)
        if scraped:
            content = scraped
    except requests.RequestException as exc:
        print(f"Scrape failed for {url}: {exc}")

    # If still too short, fetch Wikipedia/news data
    if not content or len(content) < 500:
        extra_info = fetch_company_info(name)
        if extra_info:
            content += "\n\n" + extra_info

    if not content:
        content = f"{name} ({url})"

    embedding = embed_text(content)
    metadata = {
        "name": name,
        "url": url,
        "description": content[:5000],
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    index.upsert(
        vectors=[{"id": company_id, "values": embedding, "metadata": metadata}]
    )
    print(f"Upserted {name} ({company_id}) from {url}")
