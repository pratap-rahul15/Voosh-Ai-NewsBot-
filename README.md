
# **🤖 VooshAI NewsBot** 

**VooshAI NewsBot** is a **full-stack RAG-powered chatbot** that retrieves, summarizes, and explains news articles in real-time.

It utilizes a **Retrieval-Augmented Generation (RAG) pipeline** with **Qdrant Cloud (vector database)**, **Gemini API (large language model)**, and **Upstash Redis (session history)** to deliver concise, contextual news answers.

**Visit the project at**
 
 https://voosh-ai-news-bot.vercel.app/ 


### 🚀 Features

**-> Ingests ~50 news articles into a vector database.**

**-> Embeds content with SentenceTransformers (all-MiniLM-L6-v2).**

**-> Retrieves top-k relevant articles using Qdrant Cloud**

**-> Generates answers via Google Gemini (1.5 Flash).**

**-> Stores session history in Upstash Redis (1-hour TTL).**

**-> Frontend built with React + Vite, styled with SCSS and custom chat UI.**

**-> Deployed on Render (backend) + Vercel (frontend).**

### 🛠️ RAG Pipeline Overview

****1**** - Data Ingestion

- ~50 news articles ingested into ChromaDB locally for dev.

- Embedded using SentenceTransformer("all-MiniLM-L6-v2").

****2**** - Vector Search (Using Cosine Distance)

- Later migrated to Qdrant Cloud for production.

- Stores embeddings + metadata (title, url, text).

****3**** - Generation

- Retrieved articles passed as context into Gemini API.

- Summarizes & synthesizes across multiple sources.

****4**** - Session History

- Stored in Upstash Redis for fast retrieval.

- Supports /history and /clear_session APIs.


### 🚀 Getting Started ⚙️ Backend Setup (FastAPI)

1. Clone the Repository

```
https://github.com/pratap-rahul15/Voosh-Ai-NewsBot-.git
cd Voosh-Ai-NewsBot/backend

```

2. Create a virtual environment
```
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

3.  Install the dependencies required to spin up the project.

```
pip install -r requirements.txt
```

4.  Run backend locally
```
uvicorn chatbot:app --reload --host 0.0.0.0 --port 8005
```

***Backend Endpoints***

POST /ask → Ask a question

GET /history → Retrieve session history

POST /clear_session → Reset history


### 🚀 Getting Started 🎨 Frontend Setup (React + Vite)

Go to frontend folder

```
cd ../frontend

# Install dependencies
npm install

# Run locally
npm run dev

```

***Default dev server***
```
👉 http://127.0.0.1:5173
```

### 🔑 Environment Variables

```
# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Qdrant Cloud
QDRANT_URL=https://<your-qdrant-instance>.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=news_articles

# Redis (Upstash)
REDIS_URL=rediss://default:<password>@<host>:6379

```

### 🚢 Deployment

- Backend → Render (Python FastAPI)

- Frontend → Vercel (React + Vite)

- Qdrant Cloud → Persistent vector DB

- Upstash Redis → Serverless Redis for session storage

### ✅ Example Queries

```
User: What is happening in Indian politics?
Bot: India's Supreme Court recently appointed new judges but concerns remain about gender representation........
Sources:
- NewsNews - https://www.bbc.com/news/world/asia/india
- Technology of Business - https://www.bbc.com/business/technology-of-business

```


### 🛠️ Tech Stack & Dependencies
🔹 Backend (FastAPI + Python)

- FastAPI → Backend API framework

- Uvicorn → ASGI server

- python-dotenv → Load .env configs

- redis → Redis client (with Upstash Redis for cloud)

- qdrant-client → Qdrant Cloud integration

- sentence-transformers → Embedding model (all-MiniLM-L6-v2)

- google-generativeai → Gemini LLM API

- chromadb → Local vector DB (used for initial ingestion/testing)

- requests, tqdm → Helpers for ingestion

🔹 Frontend (React + Vite)

- React 18 → Frontend framework

- Vite → Fast React build tool

- Axios → API requests

- SCSS / inline styles → Styling and chat UI

🔹 Database & Storage

- Qdrant Cloud → Persistent vector database

- ChromaDB → Local dev vector database (before migration to Qdrant)

- Upstash Redis → In-memory cache & session history

🔹 AI & NLP

- SentenceTransformers → Embeddings

- Google Gemini (1.5 Flash) → Text generation

<img width="1920" height="1030" alt="image" src="https://github.com/user-attachments/assets/58ea6fdb-a68b-489e-86cd-a3b96aa2b83c" />
<img width="1919" height="1029" alt="image" src="https://github.com/user-attachments/assets/b30fb2b3-cd57-44de-a9cb-4526ca325564" />


 🌟 Author

Made with **❤️** by **Rahul Singh**
