import os
import openai
import pinecone
from dotenv import load_dotenv

load_dotenv()

# Setup OpenAI (modern client pattern)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup Pinecone client and index (v3+)
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("index2")

def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def find_similar_competitors(description, top_k=5):
    query_vec = get_embedding(description)
    # Query Pinecone using the modern API
    result = index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    return result["matches"]

def analyze_competitors(user_company_name, competitors):
    prompt = (
    f"You are a SaaS market analyst. Analyze the following competitors of "
    f"'{user_company_name}' and for each one, provide:\n"
    " - Danger Rating (1 = not dangerous, 5 = very dangerous)\n"
    " - CX strategy\n"
    " - Target audience\n"
    " - Donor portal UX (e.g., clunky, intuitive)\n"
    " - Messaging\n"
    " - Cross-selling of financial or charitable services\n"
    " - Whether they offer a mobile website or app\n"
)
    lines = [
        f"{c['metadata']['name']}: {c['metadata']['description']}"
        for c in competitors
    ]
    context = "\n\n".join(lines)
    messages = [
        {"role": "system", "content": "You are a helpful competitor analysis agent."},
        {"role": "user", "content": prompt + "\n\n" + context}
    ]

    # Modern OpenAI Chat API call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.4
    )
    return response.choices[0].message.content
