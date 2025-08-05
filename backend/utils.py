import requests
import openai
import pinecone
from embed_and_store import upsert_website

def upsert_from_url(url, i, snippet):
    """Upsert a competitor from a URL with fallback summary, using a standard id and name."""
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
