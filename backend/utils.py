from __future__ import annotations

from urllib.parse import urlparse
from typing import Optional, Dict  # noqa: F401 (kept for future typed helpers)
import hashlib

import pinecone


# Try to import Pinecone's base exception in a version-agnostic way.
try:
    from pinecone.exceptions import PineconeException as _PineconeError  # type: ignore
except ImportError:  # narrow, no broad-except
    class _PineconeError(Exception):  # type: ignore
        """Fallback Pinecone exception base class."""


def canonicalize_url(url: str) -> str:
    """Normalize URL -> canonical host (lowercased, no leading 'www.')."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or parsed.path).lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def make_company_id(url: str) -> str:
    """Deterministic vector ID derived from the canonical host."""
    host = canonicalize_url(url)
    return f"site::{host.replace('.', '_')}"


def hash_key(s: str, length: int = 16) -> str:
    """Optional: short hash helper if you ever need it."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:length]


def vector_exists(index: pinecone.Index, vector_id: str) -> bool:
    """Return True if a vector ID already exists in Pinecone (v3 fetch)."""
    try:
        res = index.fetch(ids=[vector_id])
    except _PineconeError:
        # Treat transient Pinecone errors as "not found" to avoid blocking progress.
        return False

    # SDK may return object-like or dict-like; support both.
    vectors = getattr(res, "vectors", None)
    if vectors is None and isinstance(res, dict):
        vectors = res.get("vectors", {})

    try:
        return vector_id in (vectors or {})
    except (TypeError, KeyError, AttributeError):
        return False
