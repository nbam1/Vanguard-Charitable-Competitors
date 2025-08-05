from serpapi import GoogleSearch
import os

def find_competitor_websites(query, num_results=10):
    print("searching...")
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": os.getenv("SERPAPI_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)
    urls = []
    for result in results.get("organic_results", []):
        link = result.get("link")
        title = result.get("title", "").lower()
        # crude filter: look for likely DAF providers
        if any(k in title for k in ["fund", "charitable", "foundation", "philanthropy", "daff", "donor advised"]):
            urls.append(link)
    return urls
