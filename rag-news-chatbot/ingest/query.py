import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="news_articles")

def query_news(question, top_k=3):
    # Embed user query
    query_embedding = model.encode(question).tolist()

    # Retrieve top-k results
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    print("\n Query:", question)
    print(" Top Results:")
    for i in range(len(results["documents"][0])):
        title = results["metadatas"][0][i]["title"]
        url = results["metadatas"][0][i]["url"]
        snippet = results["documents"][0][i][:200].replace("\n", " ") + "..."
        print(f"\n {i+1}.  {title}")
        print(f"     {url}")
        print(f"     {snippet}")

if __name__ == "__main__":
    while True:
        q = input("\n Ask me about the news (or type 'exit'): ")
        if q.lower() in ["exit", "quit"]:
            break
        query_news(q)
