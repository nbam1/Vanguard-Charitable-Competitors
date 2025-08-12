from __future__ import annotations

import os
from typing import Optional, Dict

import openai
import pinecone
from dotenv import load_dotenv

from scrape_website import scrape_website
from utils import vector_exists

load_dotenv()

# OpenAI client (modern)
CLIENT = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pinecone client + index (v3+); ensure your env and index name are correct
PC = pinecone.Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV"),
)

# Use your existing index name here (must be created ahead of time with dim=1536)
INDEX_NAME = os.getenv("PINECONE_INDEX", "index2")
INDEX = PC.Index(INDEX_NAME)


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

    # Try to scrape the page; fall back to snippet if scraping fails/empty
    scraped = ""
    try:
        scraped = scrape_website(url)
    except Exception as exc:  # narrow if you raise specific errors in scraper
        print(f"Scrape failed for {url}: {exc}")

    content = scraped or fallback_summary or f"{name} ({url})"

    embedding = embed_text(content)
    metadata = {
        "name": name,
        "url": url,
        "description": content[:5000],  # keep large but safe
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    index.upsert(
        vectors=[
            {
                "id": company_id,
                "values": embedding,
                "metadata": metadata,
            }
        ]
    )
    print(f"Upserted {name} ({company_id}) from {url}")
