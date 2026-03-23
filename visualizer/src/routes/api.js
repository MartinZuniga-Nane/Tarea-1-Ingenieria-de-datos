const { Router } = require("express");

function normalizeScope(scope) {
  if (["global", "python", "java"].includes(scope)) {
    return scope;
  }
  return null;
}

function parseTop(value, fallback) {
  if (value === undefined) {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }
  return Math.min(500, Math.floor(parsed));
}

function createApiRouter(store, defaultTopN) {
  const router = Router();

  router.get("/ranking", (req, res) => {
    const scope = normalizeScope(req.query.scope || "global");
    if (!scope) {
      return res.status(400).json({ error: "scope debe ser global, python o java" });
    }

    const top = parseTop(req.query.top, defaultTopN);
    if (top === null) {
      return res.status(400).json({ error: "top debe ser un entero positivo" });
    }

    return res.json({
      scope,
      top,
      data: store.getRanking(scope, top),
    });
  });

  router.get("/stats", (req, res) => {
    return res.json(store.getStats());
  });

  return router;
}

module.exports = { createApiRouter };
