const path = require("path");
const express = require("express");
const morgan = require("morgan");

const { RankingStore } = require("./rankingStore");
const { createEventsRouter } = require("./routes/events");
const { createApiRouter } = require("./routes/api");
const { createStreamRouter } = require("./routes/stream");

const PORT = Number(process.env.PORT || 3000);
const DEFAULT_TOP_N = Number(process.env.DEFAULT_TOP_N || 10);

class StreamHub {
  constructor() {
    this.clients = new Set();
  }

  addClient(res) {
    this.clients.add(res);
    res.write(`event: connected\n`);
    res.write(`data: ${JSON.stringify({ ok: true, at: new Date().toISOString() })}\n\n`);
  }

  removeClient(res) {
    this.clients.delete(res);
  }

  broadcast(payload) {
    const eventData = `event: update\ndata: ${JSON.stringify(payload)}\n\n`;
    for (const client of this.clients) {
      client.write(eventData);
    }
  }
}

const app = express();
const store = new RankingStore();
const streamHub = new StreamHub();

app.use(morgan("dev"));
app.use(express.json({ limit: "1mb" }));

app.use("/events", createEventsRouter(store, streamHub, DEFAULT_TOP_N));
app.use("/api", createApiRouter(store, DEFAULT_TOP_N));
app.use("/stream", createStreamRouter(streamHub));
app.use(express.static(path.join(__dirname, "..", "public")));

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.use((err, _req, res, _next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({ error: "internal_server_error" });
});

app.listen(PORT, () => {
  console.log(`Visualizer listening on port ${PORT}`);
});
