from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import logging
import time

from .blob_fetcher import BlobFetcher
from .config import load_config
from .extractors.java_extractor import JavaExtractor
from .extractors.python_extractor import PythonExtractor
from .github_client import GitHubClient
from .identifier_splitter import split_identifier
from .logging_config import configure_logging
from .publisher import Publisher
from .repository_discovery import RepositoryDiscovery
from .repository_state import RepositoryState
from .tree_fetcher import TreeFetcher

logger = logging.getLogger(__name__)


class MinerService:
    def __init__(self) -> None:
        self.config = load_config()
        configure_logging(self.config.log_level)

        self.github = GitHubClient(self.config.github_token)
        self.discovery = RepositoryDiscovery(self.github, min_stars=self.config.min_stars)
        self.state = RepositoryState(self.config.state_dir)
        self.tree_fetcher = TreeFetcher(self.github, self.config.max_file_size_bytes)
        self.blob_fetcher = BlobFetcher(self.github)
        self.publisher = Publisher(self.config.visualizer_url)
        self.py_extractor = PythonExtractor()
        self.java_extractor = JavaExtractor()

    def run_forever(self) -> None:
        logger.info("Miner started. min_stars=%s", self.config.min_stars)
        try:
            while True:
                self.run_once()
                time.sleep(self.config.batch_sleep_seconds)
        except KeyboardInterrupt:
            logger.info("Miner stopped by user (Ctrl+C)")

    def run_once(self) -> None:
        processed_this_run = 0

        for repo in self.discovery.iter_repositories(self.config.max_repos_per_run * 3):
            if processed_this_run >= self.config.max_repos_per_run:
                break
            if self.state.is_processed(repo.full_name):
                continue

            payload = self._process_repository(repo.owner, repo.name, repo.full_name, repo.stars, repo.default_branch)
            if payload is None:
                continue

            self.publisher.publish(payload)
            self.state.mark_processed(repo.full_name)
            processed_this_run += 1

        logger.info("Run finished. processed_repositories=%s", processed_this_run)

    def _process_repository(
        self,
        owner: str,
        repo: str,
        full_name: str,
        stars: int,
        branch: str,
    ) -> dict | None:
        logger.info("Processing repository %s", full_name)
        try:
            files = self.tree_fetcher.list_source_files(owner, repo, branch)
        except Exception:
            logger.exception("Failed to fetch tree for %s", full_name)
            return None

        language_counts = {
            "python": Counter(),
            "java": Counter(),
        }
        files_processed = 0
        functions_found = 0

        for file_ref in files:
            source = self.blob_fetcher.fetch_blob_text(owner, repo, file_ref.sha)
            if not source:
                continue

            if file_ref.language == "python":
                names = self.py_extractor.extract_function_names(source)
            else:
                names = self.java_extractor.extract_method_names(source)

            if not names:
                continue

            files_processed += 1
            functions_found += len(names)
            for name in names:
                for token in split_identifier(name):
                    language_counts[file_ref.language][token] += 1

        payload = {
            "repo": full_name,
            "stars": stars,
            "files_processed": files_processed,
            "functions_found": functions_found,
            "language_counts": {
                "python": dict(language_counts["python"]),
                "java": dict(language_counts["java"]),
            },
            "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        logger.info(
            "Processed repo=%s files_processed=%s functions_found=%s",
            full_name,
            files_processed,
            functions_found,
        )
        return payload


if __name__ == "__main__":
    MinerService().run_forever()
