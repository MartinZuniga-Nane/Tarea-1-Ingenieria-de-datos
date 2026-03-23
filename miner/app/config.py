from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class MinerConfig:
    github_token: str
    visualizer_url: str
    state_dir: str
    min_stars: int
    max_repos_per_run: int
    batch_sleep_seconds: float
    max_file_size_bytes: int
    log_level: str



def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)



def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)



def load_config() -> MinerConfig:
    return MinerConfig(
        github_token=os.getenv("GITHUB_TOKEN", "").strip(),
        visualizer_url=os.getenv("VISUALIZER_URL", "http://visualizer:3000/events").strip(),
        state_dir=os.getenv("STATE_DIR", "/data").strip(),
        min_stars=_env_int("MIN_STARS", 1000),
        max_repos_per_run=_env_int("MAX_REPOS_PER_RUN", 20),
        batch_sleep_seconds=_env_float("BATCH_SLEEP_SECONDS", 5.0),
        max_file_size_bytes=_env_int("MAX_FILE_SIZE_BYTES", 250_000),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
    )
