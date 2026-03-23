const { Router } = require("express");

function createStreamRouter(streamHub) {
  const router = Router();

  router.get("/", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders?.();

    streamHub.addClient(res);

    req.on("close", () => {
      streamHub.removeClient(res);
    });
  });

  return router;
}

module.exports = { createStreamRouter };
