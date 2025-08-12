from __future__ import annotations

from urllib.parse import urlparse
import hashlib
import requests
import openai
import pinecone
from typing import Optional, Dict

from embed_and_store import upsert_website  # uses deterministic ID inside


def canonicalize_url(url: str) -> str:
    """Normalize URL -> canonical host (lowercased, no www)."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or parsed.path).lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def make_company_id(url: str) -> str:
    """Deterministic vector ID derived from canonical host."""
    host = canonicalize_url(url)
    return f"site::{host.replace('.', '_')}"


def hash_key(s: str, length: int = 16) -> str:
    """Optional: short hash helper if you ever need it."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:length]


def vector_exists(index: pinecone.Index, vector_id: str) -> bool:
    """Check if a vector ID already exists in Pinecone (v3 fetch)."""
    try:
        res = index.fetch(ids=[vector_id])
        # SDK can return an object or dict; handle both
        vecs = getattr(res, "vectors", None) or res.get("vectors", {})
        return vector_id in vecs
    except Exception:
        # On transient errors, be conservative: treat as not existing
        return False


def upsert_from_url(
    index: pinecone.Index,
    url: str,
    i: int,
    snippet: str = "",
    name: Optional[str] = None,
    extra_metadata: Optional[Dict[str, str]] = None,
) -> None:
    """
    Build stable ID + friendly name from URL, then upsert once.
    Any errors are narrowed and logged (pylint-friendly).
    """
    domain = canonicalize_url(url)
    company_id = make_company_id(url)
    display_name = name or domain

    try:
        upsert_website(
            index=index,
            url=url,
            company_id=company_id,
            name=display_name,
            fallback_summary=snippet,
            extra_metadata=extra_metadata or {"domain": domain},
        )
    except (
        requests.RequestException,
        openai.OpenAIError,
        pinecone.core.client.exceptions.PineconeException,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"Could not upsert {url} ({company_id}): {exc}")
