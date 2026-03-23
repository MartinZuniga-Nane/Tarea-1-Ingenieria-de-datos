from __future__ import annotations

from pathlib import Path

from .file_state_store import JsonFileStore


class RepositoryState:
    def __init__(self, state_dir: str):
        base = Path(state_dir)
        self.processed_store = JsonFileStore(base / "processed_repos.json", {"repos": []})
        self.progress_store = JsonFileStore(base / "miner_progress.json", {"star_ranges": []})

    def is_processed(self, repo_full_name: str) -> bool:
        data = self.processed_store.read()
        return repo_full_name in set(data.get("repos", []))

    def mark_processed(self, repo_full_name: str) -> None:
        data = self.processed_store.read()
        repos = set(data.get("repos", []))
        repos.add(repo_full_name)
        self.processed_store.write({"repos": sorted(repos)})

    def get_progress(self) -> dict:
        return self.progress_store.read()

    def save_progress(self, progress: dict) -> None:
        self.progress_store.write(progress)
