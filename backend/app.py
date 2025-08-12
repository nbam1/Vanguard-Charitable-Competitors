from __future__ import annotations

import os
import asyncio
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from serpapi import GoogleSearch

import pinecone

from competitor_agent import find_similar_competitors, analyze_competitors
from embed_and_store import INDEX  # same Index instance
from utils import canonicalize_url, upsert_from_url

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

            # deterministic ID inside upsert
            upsert_from_url(
                index=INDEX,
                url=url,
                i=i,
                snippet=snippet,
                extra_metadata={"source": "serpapi"},
            )

    # 3) Retrieve similar
    matches = find_similar_competitors(company_desc)

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
