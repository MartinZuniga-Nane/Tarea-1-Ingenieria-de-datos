from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, token: str):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-miner/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=30)
        if response.status_code >= 400:
            logger.error("GitHub request failed (%s): %s", response.status_code, response.text)
            response.raise_for_status()
        return response.json()

    def get_repo_default_branch(self, owner: str, repo: str) -> str:
        data = self.get(f"/repos/{owner}/{repo}")
        return data.get("default_branch", "main")
