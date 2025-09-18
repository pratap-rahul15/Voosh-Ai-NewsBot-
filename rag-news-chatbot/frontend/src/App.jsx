import { useState, useEffect } from "react";
import axios from "axios";

// Auto-detect backend URL
const API_URL =
  process.env.NODE_ENV === "development"
    ? "http://127.0.0.1:8005"
    : "https://voosh-ai-newsbot.onrender.com";

function App() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  //  Load history on startup
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_URL}/history`);
        setHistory(res.data.history);
      } catch (err) {
        console.error("Error fetching history:", err);
      }
    };
    fetchHistory();
  }, []);

  //  Ask backend
  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/ask`, { query });
      setHistory(res.data.history);
      setQuery("");
    } catch (err) {
      setHistory((prev) => [...prev, "⚠️ Error connecting to backend."]);
    } finally {
      setLoading(false);
    }
  };

  //  Reset session
  const handleReset = async () => {
    try {
      const res = await axios.post(`${API_URL}/clear_session`);
      setHistory(res.data.history);
    } catch (err) {
      console.error("Reset failed:", err);
    }
  };

  //  Chat bubble renderer
  const renderMessage = (msg, i) => {
    if (typeof msg !== "string") return null;

    const isUser = msg.startsWith("You:");
    const isBot = msg.startsWith("Bot:");

    let content = msg.replace(/^You:\s*/, "").replace(/^Bot:\s*/, "");

    // Split summary and sources
    let mainText = content;
    let sourcesBlock = "";
    if (isBot && content.includes("Sources:")) {
      [mainText, sourcesBlock] = content.split("Sources:");
    }

    return (
      <div
        key={i}
        style={{
          display: "flex",
          justifyContent: isUser ? "flex-end" : "flex-start",
          marginBottom: "10px",
        }}
      >
        <div
          style={{
            maxWidth: "75%",
            padding: "10px 14px",
            borderRadius: "12px",
            background: isUser ? "#2563eb" : "#e5e7eb",
            color: isUser ? "white" : "black",
            textAlign: "left",
            whiteSpace: "pre-wrap",
          }}
        >
          <p style={{ margin: 0 }}>{mainText.trim()}</p>

          
          {isBot && sourcesBlock && (
            <div style={{ marginTop: "8px" }}>
              <strong>Sources:</strong>
              <ul style={{ marginTop: "4px", paddingLeft: "18px" }}>
                {sourcesBlock
                  .trim()
                  .split("\n")
                  .map((line) => line.replace(/^[\*\-\s]+/, "").trim())
                  .filter((line) => line.length > 0)
                  .map((src, j) => {
                    const parts = src.split(" - ");
                    const title = parts[0] || "Link";
                    let url = parts[1] || parts[0];
                    if (
                      url &&
                      !url.startsWith("http://") &&
                      !url.startsWith("https://")
                    ) {
                      url = "https://" + url;
                    }
                    return (
                      <li key={j}>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: "#2563eb",
                            textDecoration: "underline",
                          }}
                        >
                          {title}
                        </a>
                      </li>
                    );
                  })}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "#f9fafb",
        padding: "20px",
      }}
    >
      <div
        style={{
          background: "white",
          padding: "30px",
          borderRadius: "12px",
          boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
          maxWidth: "700px",
          width: "100%",
        }}
      >
        <h1 style={{ textAlign: "center", fontSize: "28px", marginBottom: "10px" }}>
          VooshAI NewsBot 🤖
        </h1>
        <p
          style={{
            textAlign: "center",
            fontSize: "16px",
            color: "#555",
            marginBottom: "20px",
          }}
        >
          An AI-powered chatbot that retrieves, summarizes, and explains news
          articles in real-time using RAG (Retrieval-Augmented Generation).
        </p>

        {/* Chat Window */}
        <div
          style={{
            background: "#f3f4f6",
            borderRadius: "8px",
            padding: "15px",
            height: "350px",
            overflowY: "auto",
            marginBottom: "20px",
            fontSize: "15px",
          }}
        >
          {history.length === 0 ? (
            <p style={{ textAlign: "center", color: "#777" }}>
              Start chatting to see responses...
            </p>
          ) : (
            history.map((msg, i) => renderMessage(msg, i))
          )}
        </div>

        
        <div style={{ display: "flex", gap: "10px" }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask about the news..."
            style={{
              flex: 1,
              padding: "12px",
              border: "1px solid #ddd",
              borderRadius: "6px",
              fontSize: "15px",
            }}
          />
          <button
            onClick={handleAsk}
            disabled={loading}
            style={{
              padding: "12px 18px",
              border: "none",
              borderRadius: "6px",
              background: "#2563eb",
              color: "white",
              cursor: "pointer",
              fontSize: "15px",
            }}
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
          <button
            onClick={handleReset}
            style={{
              padding: "12px 18px",
              border: "none",
              borderRadius: "6px",
              background: "#ef4444",
              color: "white",
              cursor: "pointer",
              fontSize: "15px",
            }}
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
