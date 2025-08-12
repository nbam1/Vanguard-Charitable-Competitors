from __future__ import annotations

from typing import Optional, Dict

import requests
import openai
import pinecone

from embed_and_store import upsert_website
from utils import canonicalize_url, make_company_id


# Try to import Pinecone's base exception in a version-agnostic way.
try:
    from pinecone.exceptions import PineconeException as _PineconeError  # type: ignore
except ImportError:
    class _PineconeError(Exception):  # type: ignore
        """Fallback Pinecone exception base class."""


def upsert_from_url(
    index: pinecone.Index,
    url: str,
    *,
    snippet: str = "",
    name: Optional[str] = None,
    extra_metadata: Optional[Dict[str, str]] = None,
) -> None:
    """
    Build a stable ID + friendly name from URL, then upsert once.
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
            extra_metadata=(extra_metadata or {"domain": domain}),
        )
    except (
        requests.RequestException,
        openai.OpenAIError,
        _PineconeError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"Could not upsert {url} ({company_id}): {exc}")
