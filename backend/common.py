from __future__ import annotations

import os

import openai
import pinecone
from dotenv import load_dotenv

load_dotenv()

# OpenAI client (v1+)
CLIENT = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pinecone client (v3+)
PC = pinecone.Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV"),
)

INDEX_NAME = os.getenv("PINECONE_INDEX", "index2")
INDEX = PC.Index(INDEX_NAME)
