from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterator

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RepoInfo:
    full_name: str
    owner: str
    name: str
    stars: int
    default_branch: str


class RepositoryDiscovery:
    """Discovers repositories in descending stars, with simple star-range partitioning."""

    def __init__(self, github_client: GitHubClient, min_stars: int):
        self.github_client = github_client
        self.min_stars = min_stars

    def _search(self, query: str, per_page: int = 100, page: int = 1) -> dict:
        return self.github_client.get(
            "/search/repositories",
            params={
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            },
        )

    def iter_repositories(self, max_repos: int) -> Iterator[RepoInfo]:
        yielded = 0
        # Strategy: descending star windows to avoid search 1000 results ceiling.
        # This is simple and extensible for a coursework setting.
        ranges = [
            (100_000, None),
            (50_000, 99_999),
            (20_000, 49_999),
            (10_000, 19_999),
            (5_000, 9_999),
            (self.min_stars, 4_999),
        ]
        for low, high in ranges:
            if low < self.min_stars:
                continue
            star_filter = f"stars:{low}..{high}" if high is not None else f"stars:>={low}"
            query = f"is:public archived:false {star_filter}"
            for page in range(1, 11):  # 10 * 100 = 1000 API ceiling per query
                data = self._search(query=query, page=page)
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    full_name = item["full_name"]
                    owner, repo = full_name.split("/", 1)
                    yield RepoInfo(
                        full_name=full_name,
                        owner=owner,
                        name=repo,
                        stars=int(item.get("stargazers_count", 0)),
                        default_branch=item.get("default_branch", "main"),
                    )
                    yielded += 1
                    if yielded >= max_repos:
                        return
