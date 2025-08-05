from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from competitor_agent import find_similar_competitors, analyze_competitors
from embed_and_store import upsert_website
from search_competitors import find_competitor_websites

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-and-analyze")
async def search_and_analyze(request: Request):
    data = await request.json()
    user_company_name = data["company_name"]
    user_company_description = data["company_description"]

    # Search for competitors (web)
    search_query = "top donor advised fund providers"
    candidate_urls = find_competitor_websites(search_query, num_results=10)
    # Upsert competitors (add fallback snippet/summary logic here if needed)
    for i, url in enumerate(candidate_urls):
        domain = url.split("//")[-1].split("/")[0]
        company_id = f"{domain.replace('.', '_')}_{i}"
        name = domain.replace("www.", "")
        try:
            upsert_website(company_id, name, url)
        except Exception as e:
            print(f"Could not upsert {url}: {e}")

    # Query and analyze
    matches = find_similar_competitors(user_company_description)
    report = analyze_competitors(user_company_name, matches)
    # Return both the matches and the analysis
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