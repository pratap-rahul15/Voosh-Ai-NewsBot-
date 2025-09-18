import os, json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "news_articles")
EMBED_DIM = 384

if not QDRANT_URL:
    raise ValueError("Set QDRANT_URL in .env")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

print("(Re)creating collection:", QDRANT_COLLECTION)
client.recreate_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=rest.VectorParams(size=EMBED_DIM, distance=rest.Distance.COSINE),
)

ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "data", "articles.json")
with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

BATCH = []
IDX = 0
BATCH_SIZE = 64
for a in tqdm(articles, desc="Preparing"):
    content = a.get("content") or a.get("text") or a.get("body", "")
    title = (a.get("title") or "")[:250]
    url = a.get("url") or a.get("link") or ""
    payload = {"title": title, "url": url, "source": a.get("source", "")}
    vector = model.encode(content).tolist()
    pt = rest.PointStruct(id=IDX, vector=vector, payload={**payload, "text": content[:4000]})
    BATCH.append(pt)
    IDX += 1
    if len(BATCH) >= BATCH_SIZE:
        client.upsert(collection_name=QDRANT_COLLECTION, points=BATCH)
        BATCH = []

if BATCH:
    client.upsert(collection_name=QDRANT_COLLECTION, points=BATCH)

print("Ingested", IDX, "articles.")
