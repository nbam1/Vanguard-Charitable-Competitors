from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scrape_website import scrape_website
from embed_and_store import upsert_website
from competitor_agent import find_similar_competitors, analyze_competitors

app = FastAPI()

# CORS setup — adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url:
        return {"error": "No URL provided."}

    try:
        # Step 1: Scrape website
        scraped_text = scrape_website(url)

        # Step 2: Embed and store it in Pinecone
        upsert_website(scraped_text, url)

        # Step 3: Retrieve similar competitors
        competitors = find_similar_competitors(url)

        # Step 4: Analyze them via OpenAI
        analysis = analyze_competitors(url, competitors)

        return {"response": analysis}

    except Exception as e:
        return {"error": str(e)}
