import os
import requests
import openai
import pinecone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from embed_and_store import upsert_website
from competitor_agent import find_similar_competitors, analyze_competitors
from serpapi import GoogleSearch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_competitor_sites(query, num_results=10):
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": os.getenv("SERPAPI_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])

def process_competitors(organic_results):
    for i, result in enumerate(organic_results):
        url = result.get("link")
        snippet = result.get("snippet", "")
        if not url:
            continue
        domain = url.split("//")[-1].split("/")[0]
        company_id = f"{domain.replace('.', '_')}_{i}"
        name = domain.replace("www.", "")
        try:
            upsert_website(company_id, name, url, fallback_summary=snippet)
        except (
            requests.RequestException,
            openai.OpenAIError,
            pinecone.core.client.exceptions.PineconeException,
            ValueError,
        ) as e:
            print(f"Could not upsert {url}: {e}")

@app.post("/search-and-analyze")
async def search_and_analyze(request: Request):
    data = await request.json()
    user_company_name = data.get("company_name")
    user_company_description = data.get("company_description")

    if not user_company_name or not user_company_description:
        return {"error": "Missing company_name or company_description."}

    # Step 1: Search for competitor websites
    organic_results = search_competitor_sites("top donor advised fund providers", 10)

    # Step 2: Upsert all competitors
    process_competitors(organic_results)

    # Step 3: Find similar competitors
    matches = find_similar_competitors(user_company_description)

    # Step 4: Analyze competitors
    report = analyze_competitors(user_company_name, matches)

    # Step 5: Return structured result
    return {
        "matches": [
            {
                "id": m['id'],
                "score": m['score'],
                "name": m['metadata']['name'],
                "description": m['metadata'].get('description', '')
            } for m in matches
        ],
        "report": report
    }
