from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, visualizer_url: str):
        self.visualizer_url = visualizer_url
        self.session = requests.Session()

    def publish(self, payload: dict) -> None:
        response = self.session.post(self.visualizer_url, json=payload, timeout=20)
        if response.status_code >= 400:
            logger.error("Publish failed (%s): %s", response.status_code, response.text)
            response.raise_for_status()
        logger.info("Published batch for repo=%s", payload.get("repo"))
