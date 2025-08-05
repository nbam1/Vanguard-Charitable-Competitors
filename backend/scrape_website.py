import re
import requests
from bs4 import BeautifulSoup

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def scrape_website(url, max_chars=5000):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(["p", "h1", "h2", "h3", "h4"])
    raw_text = " ".join([el.get_text() for el in elements])
    return clean_text(raw_text[:max_chars])
