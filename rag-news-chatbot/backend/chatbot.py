import os, json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import google.generativeai as genai
import redis


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# Gemini API Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Set GEMINI_API_KEY in .env")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Qdrant Cloud Setup
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "news_articles")
if not QDRANT_URL:
    raise ValueError("Set QDRANT_URL in .env")

qclient = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
print("Qdrant:", QDRANT_URL, "collection:", QDRANT_COLLECTION)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Redis Cloud (Upstash) Setup 
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    r = redis.from_url(REDIS_URL, decode_responses=True)
else:
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

HISTORY_KEY = "chat_history"

#  FastAPI Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Qdrant Cloud Search 
def search_qdrant(query: str, top_k: int = 3):
    q_vec = embed_model.encode(query).tolist()
    results = qclient.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=q_vec,
        limit=top_k,
        with_payload=True,
    )
    hits = []
    for item in results:
        payload = item.payload or {}
        hits.append({
            "title": payload.get("title", "Untitled"),
            "url": payload.get("url", ""),
            "snippet": (payload.get("text") or "")[:600].replace("\n", " "),
            "score": getattr(item, "score", None)
        })
    return hits

# API Routes Defined.
@app.post("/ask")
async def ask(payload: dict):
    question = (payload.get("query") or "").strip()
    if not question:
        return {"history": [], "answer": " Please provide a query.", "sources": []}

    hits = search_qdrant(question, top_k=3)
    if not hits:
        answer = " Sorry, I couldn't find relevant news articles in the database."
        r.rpush(HISTORY_KEY, f"You: {question}")
        r.rpush(HISTORY_KEY, f"Bot: {answer}")
        return {"history": r.lrange(HISTORY_KEY, 0, -1), "answer": answer, "sources": []}

    context_parts, sources = [], []
    for i, h in enumerate(hits, start=1):
        context_parts.append(
            f"Article {i}:\nTitle: {h['title']}\nURL: {h['url']}\nSnippet: {h['snippet']}"
        )
        if h.get("url"):
            sources.append({"title": h["title"], "url": h["url"]})

    context = "\n\n".join(context_parts)
    prompt = f"""You are a helpful news assistant.
You will be given up to 3 retrieved news articles. For each article, write 2–3 sentences summarizing the key point.
After summarizing each article, write a short 'Final Note' synthesizing across all articles.
At the end, include a 'Sources:' section listing the article URLs.

Here are the articles:
{context}

Question: {question}
"""
    resp = gemini_model.generate_content(prompt)
    summary = resp.text if resp and resp.text else "No answer generated."

    sources_text_lines = []
    for s in sources:
        clean_url = s["url"].lstrip("* ").strip()
        sources_text_lines.append(f"{s['title']} - {clean_url}")
    sources_text = "\n".join(sources_text_lines)
    answer = f"{summary}\n\nSources:\n{sources_text}"

    r.rpush(HISTORY_KEY, f"You: {question}")
    r.rpush(HISTORY_KEY, f"Bot: {answer}")

    return {"history": r.lrange(HISTORY_KEY, 0, -1), "answer": answer, "sources": sources}

@app.post("/clear_session")
async def clear_session():
    r.delete(HISTORY_KEY)
    return {"message": "Chat history cleared", "history": []}

@app.get("/history")
async def get_history():
    history = r.lrange(HISTORY_KEY, 0, -1)
    return {"history": history}
