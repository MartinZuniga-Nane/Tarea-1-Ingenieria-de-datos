from __future__ import annotations

from dataclasses import dataclass
import logging

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


IGNORED_DIR_FRAGMENTS = (
    "/node_modules/",
    "/vendor/",
    "/dist/",
    "/build/",
    "/target/",
)


@dataclass(frozen=True)
class SourceFileRef:
    path: str
    sha: str
    size: int
    language: str


class TreeFetcher:
    def __init__(self, github_client: GitHubClient, max_file_size_bytes: int):
        self.github_client = github_client
        self.max_file_size_bytes = max_file_size_bytes

    def _infer_language(self, path: str) -> str | None:
        lower = path.lower()
        if lower.endswith(".py"):
            return "python"
        if lower.endswith(".java"):
            return "java"
        return None

    def _is_noise_path(self, path: str) -> bool:
        wrapped = f"/{path}/"
        return any(fragment in wrapped for fragment in IGNORED_DIR_FRAGMENTS)

    def list_source_files(self, owner: str, repo: str, branch: str) -> list[SourceFileRef]:
        tree = self.github_client.get(f"/repos/{owner}/{repo}/git/trees/{branch}", params={"recursive": "1"})
        refs: list[SourceFileRef] = []
        for entry in tree.get("tree", []):
            if entry.get("type") != "blob":
                continue
            path = entry.get("path", "")
            if self._is_noise_path(path):
                continue
            language = self._infer_language(path)
            if language is None:
                continue
            size = int(entry.get("size", 0))
            if size > self.max_file_size_bytes:
                continue
            refs.append(
                SourceFileRef(
                    path=path,
                    sha=entry["sha"],
                    size=size,
                    language=language,
                )
            )
        return refs
