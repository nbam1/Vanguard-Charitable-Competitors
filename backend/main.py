import os
from utils import upsert_from_url
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
    if not url:
        continue
    upsert_from_url(url, i, snippet)

# 3. Run your usual analysis pipeline
matches = find_similar_competitors(user_company_description)
for m in matches:
    print(f"ID: {m['id']}, Score: {m['score']}, Name: {m['metadata']['name']}")

report = analyze_competitors(user_company_name, matches)
print("=== Competitor Analysis ===\n")
print(report)
