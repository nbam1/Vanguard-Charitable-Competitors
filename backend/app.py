from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

from common import INDEX  # same Index instance
from competitor_agent import analyze_competitors, find_similar_competitors
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from serpapi import GoogleSearch
from services import upsert_from_url
from utils import canonicalize_url

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set your frontend origin(s) in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_UPSERT_LOCK = asyncio.Lock()
_SEEN_HOSTS: set[str] = set()  # per-process guard to avoid duplicates in one run


def find_competitor_websites(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """SerpAPI Google search to get organic results."""
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": os.getenv("SERPAPI_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", []) or []


@app.post("/search-and-analyze")
async def search_and_analyze(request: Request) -> Dict[str, Any]:
    data = await request.json()
    company_name = data.get("company_name")
    company_desc = data.get("company_description")
    # Allow the frontend to control how many competitors to retrieve
    try:
        top_k = int(data.get("top_k", 10))
    except (TypeError, ValueError):
        top_k = 10
    # clamp to a safe range
    top_k = max(1, min(top_k, 50))

    if not company_name or not company_desc:
        return {"error": "Missing company_name or company_description."}

    # 1) Find candidate sites
    organic = find_competitor_websites("top donor advised fund providers", 10)

    # 2) Upsert (idempotent) with a lock + seen set (per-process)
    async with _UPSERT_LOCK:
        for i, r in enumerate(organic):
            url = r.get("link")
            snippet = r.get("snippet", "")
            if not url:
                continue
            host = canonicalize_url(url)
            if host in _SEEN_HOSTS:
                continue
            _SEEN_HOSTS.add(host)

            upsert_from_url(
                index=INDEX,
                url=url,
                snippet=snippet,
                extra_metadata={"source": "serpapi", "rank": i},
            )

    # 3) Retrieve similar
    matches = find_similar_competitors(company_desc, top_k=top_k)

    # 4) Analyze with LLM
    report = analyze_competitors(company_name, matches)

    return {
        "matches": [
            {
                "id": m["id"],
                "score": m["score"],
                "name": m["metadata"].get("name", m["id"]),
                "description": m["metadata"].get("description", ""),
                "url": m["metadata"].get("url", ""),
            }
            for m in matches
        ],
        "report": report,
    }
