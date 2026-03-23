const { Router } = require("express");

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validatePayload(payload) {
  if (!isObject(payload)) {
    return "Payload debe ser un objeto JSON";
  }

  if (typeof payload.repo !== "string" || payload.repo.trim() === "") {
    return "Campo 'repo' inválido";
  }

  if (!isObject(payload.language_counts)) {
    return "Campo 'language_counts' inválido";
  }

  const python = payload.language_counts.python;
  const java = payload.language_counts.java;

  if ((python !== undefined && !isObject(python)) || (java !== undefined && !isObject(java))) {
    return "'language_counts.python' y 'language_counts.java' deben ser objetos";
  }

  return null;
}

function createEventsRouter(store, streamHub, defaultTopN) {
  const router = Router();

  router.post("/", (req, res) => {
    const payload = req.body;
    const error = validatePayload(payload);

    if (error) {
      return res.status(400).json({ error });
    }

    store.ingestEvent(payload);

    const snapshot = store.snapshot(defaultTopN);
    streamHub.broadcast(snapshot);

    return res.status(202).json({ status: "accepted" });
  });

  return router;
}

module.exports = { createEventsRouter };
