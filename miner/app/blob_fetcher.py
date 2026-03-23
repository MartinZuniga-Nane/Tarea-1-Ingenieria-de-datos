from __future__ import annotations

import base64
import logging

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


class BlobFetcher:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def fetch_blob_text(self, owner: str, repo: str, sha: str) -> str:
        blob = self.github_client.get(f"/repos/{owner}/{repo}/git/blobs/{sha}")
        content = blob.get("content", "")
        encoding = blob.get("encoding", "")
        if encoding == "base64":
            try:
                return base64.b64decode(content).decode("utf-8", errors="ignore")
            except Exception:
                logger.exception("Failed to decode blob %s/%s sha=%s", owner, repo, sha)
                return ""
        return str(content)
