const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const { spawn } = require("child_process");
const Redis = require("ioredis");

const app = express();
app.use(cors());
app.use(bodyParser.json());

const redis = new Redis(); 

//  POST /chat/:sessionId
app.post("/chat/:sessionId", async (req, res) => {
  const { sessionId } = req.params;
  const { question } = req.body;

  if (!question) return res.status(400).json({ error: "Question is required" });


  const py = spawn("python", ["../ingest/chatbot.py", question]);

  let answer = "";
  py.stdout.on("data", (data) => {
    answer += data.toString();
  });

  py.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  py.on("close", async (code) => {
    console.log(`Python exited with code ${code}`);

    // save chat history in Redis memory.
    await redis.rpush(
      `chat:${sessionId}`,
      JSON.stringify({ role: "user", text: question })
    );
    await redis.rpush(
      `chat:${sessionId}`,
      JSON.stringify({ role: "bot", text: answer })
    );
    await redis.expire(`chat:${sessionId}`, 3600); // 1h is the TTL for each session.

    res.json({ answer });
  });
});

//  GET /history/:sessionId
app.get("/history/:sessionId", async (req, res) => {
  const { sessionId } = req.params;
  const history = await redis.lrange(`chat:${sessionId}`, 0, -1);
  res.json(history.map((h) => JSON.parse(h)));
});

//  DELETE /history/:sessionId
app.delete("/history/:sessionId", async (req, res) => {
  const { sessionId } = req.params;
  await redis.del(`chat:${sessionId}`);
  res.json({ message: "Session cleared" });
});

const PORT = 5000;
app.listen(PORT, () => console.log(` Backend running on port ${PORT}`));



