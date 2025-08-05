import os
import requests
import openai
import pinecone
from dotenv import load_dotenv
from scrape_website import scrape_website

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("index2")

def embed_text(text):
    response = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return response.data[0].embedding

def upsert_website(company_id, name, url, fallback_summary=None):
    try:
        scraped = scrape_website(url)
    except (requests.RequestException, ValueError) as e:
        print(f"Scraping failed for {url}: {e}")
        scraped = ""
    # Use fallback if scraping failed or result is too short
    if not scraped or len(scraped) < 100:
        if fallback_summary and len(fallback_summary) > 20:
            print(f"Using Google snippet as fallback for {name}: {fallback_summary[:100]}...")
            content = fallback_summary
        else:
            # Last resort: Use GPT to synthesize a summary
            prompt = (
                f"Summarize what '{name}' does in the donor-advised fund or charitable sector. "
                "Mention likely user experience, target audience, and key services."
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            print(f"Using GPT-generated summary for {name}: {content[:100]}...")
    else:
        content = scraped
    embedding = embed_text(content)
    index.upsert(
        vectors=[{
            "id": company_id,
            "values": embedding,
            "metadata": {"name": name, "description": content}
        }]
    )
    print(f"Upserted {name} from {url}")
    