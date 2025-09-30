"""Configuration utilities for the story reader application."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"


@dataclass(frozen=True)
class AppConfig:
    """Typed configuration for the application."""

    temp_file_folder: Path
    output_video_folder: Path
    stock_video_footage_folder: Path
    words_per_line: int
    speed: float
    model_size: str
    clip_length_cutoff: int

    def ensure_directories(self) -> None:
        """Ensure that all directories referenced by the configuration exist."""

        for directory in (
            self.temp_file_folder,
            self.output_video_folder,
            self.stock_video_footage_folder,
        ):
            directory.mkdir(parents=True, exist_ok=True)


_CONFIG_CACHE: Optional[AppConfig] = None


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _coerce_config(raw_config: Dict[str, Any]) -> AppConfig:
    return AppConfig(
        temp_file_folder=_resolve_path(raw_config["temp_file_folder"]),
        output_video_folder=_resolve_path(raw_config["output_video_folder"]),
        stock_video_footage_folder=_resolve_path(
            raw_config["stock_video_footage_folder"]
        ),
        words_per_line=int(raw_config["words_per_line"]),
        speed=float(raw_config["speed"]),
        model_size=str(raw_config["model_size"]),
        clip_length_cutoff=int(raw_config["clip_length_cutoff"]),
    )


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    """Load configuration from a JSON file."""

    with path.open("r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)
    return _coerce_config(raw_config)


def get_config(force_reload: bool = False) -> AppConfig:
    """Return the cached configuration, loading it from disk if required."""

    global _CONFIG_CACHE
    if force_reload or _CONFIG_CACHE is None:
        _CONFIG_CACHE = load_config()
        _CONFIG_CACHE.ensure_directories()
    return _CONFIG_CACHE


__all__ = ["AppConfig", "get_config", "load_config", "PROJECT_ROOT", "CONFIG_PATH"]
