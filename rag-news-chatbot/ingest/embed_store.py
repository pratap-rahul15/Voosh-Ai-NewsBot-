import json
import os
import chromadb
from sentence_transformers import SentenceTransformer

ARTICLES_PATH = os.path.join("data", "articles.json")

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Chroma client for local persistent storage.
client = chromadb.PersistentClient(path="chroma_db")

# Get or create collection
collection = client.get_or_create_collection(name="news_articles")

# Load articles from variosus sources.
with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f" Loaded {len(articles)} articles from {ARTICLES_PATH}")

# Delete existing records if present
existing = collection.get()
if existing["ids"]:
    collection.delete(ids=existing["ids"])
    print(f"🗑️ Deleted {len(existing['ids'])} old records")

# Insert new articles
for idx, article in enumerate(articles):
    text = f"{article['title']} {article['content']}"
    embedding = model.encode(text).tolist()

    collection.add(
        ids=[str(idx)],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{"title": article["title"], "url": article["url"]}],
    )

print(f" Stored {len(articles)} articles in ChromaDB at chroma_db")
