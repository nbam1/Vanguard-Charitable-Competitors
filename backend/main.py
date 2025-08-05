import os
import requests
import openai
import pinecone
from embed_and_store import upsert_website
from competitor_agent import find_similar_competitors, analyze_competitors
from serpapi import GoogleSearch

print("Loaded OpenAI Key:", os.getenv("OPENAI_API_KEY"))

user_company_name = "Vanguard Charitable"
user_company_description = (
    "A leading sponsor of donor-advised funds focused on philanthropic giving "
    "with a user-friendly digital experience."
)

search_query = "top donor advised fund providers"
candidate_results = []

# Direct use of SerpAPI so we get snippets
params = {
    "engine": "google",
    "q": search_query,
    "num": 10,
    "api_key": os.getenv("SERPAPI_KEY")
}
search = GoogleSearch(params)
results = search.get_dict()
for i, result in enumerate(results.get("organic_results", [])):
    url = result.get("link")
    snippet = result.get("snippet", "")
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

# 3. Run your usual analysis pipeline
matches = find_similar_competitors(user_company_description)
for m in matches:
    print(f"ID: {m['id']}, Score: {m['score']}, Name: {m['metadata']['name']}")

report = analyze_competitors(user_company_name, matches)
print("=== Competitor Analysis ===\n")
print(report)
