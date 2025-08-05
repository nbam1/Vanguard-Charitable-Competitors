from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from embed_and_store import upsert_website
from competitor_agent import run_agent
from scrape_website import scrape_website

app = FastAPI()

# Allow frontend requests (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_website(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url:
        return {"error": "No URL provided."}

    try:
        # Step 1: Scrape the content from the URL
        scraped_text = scrape_website(url)

        # Step 2: Embed and store the scraped text
        upsert_website(scraped_text, url)

        # Step 3: Run the GPT-based agent
        response = run_agent(url)

        return {"response": response}
    
    except Exception as e:
        return {"error": str(e)}