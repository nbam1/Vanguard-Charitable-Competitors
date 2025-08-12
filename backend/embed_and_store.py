from __future__ import annotations

from typing import Optional, Dict

import requests
import pinecone

from common import CLIENT, INDEX  # single source of truth
from scrape_website import scrape_website
from utils import vector_exists


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
    """
    Idempotent upsert: skips if the vector ID already exists.
    Scrapes if needed, embeds, and upserts with metadata.
    """
    if vector_exists(index, company_id):
        print(f"Skip (exists): {url} -> {company_id}")
        return

    # Try to scrape the page; fall back to snippet if scraping fails/empty.
    content = fallback_summary
    try:
        scraped = scrape_website(url)
        if scraped:
            content = scraped
    except requests.RequestException as exc:
        print(f"Scrape failed for {url}: {exc}")

    if not content:
        content = f"{name} ({url})"

    embedding = embed_text(content)
    metadata = {
        "name": name,
        "url": url,
        "description": content[:5000],  # keep large but safe
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    index.upsert(
        vectors=[{"id": company_id, "values": embedding, "metadata": metadata}]
    )
    print(f"Upserted {name} ({company_id}) from {url}")
