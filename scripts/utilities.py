"""Utility helpers for managing project assets."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pytube import YouTube

from configuration import AppConfig, get_config

CONFIG = get_config()


def download_video(
    url: str,
    output_directory: Optional[Path] = None,
    filename: Optional[str] = None,
    config: AppConfig | None = None,
) -> Path:
    """Download a video from YouTube to the configured stock footage directory."""

    cfg = config or CONFIG
    target_directory = output_directory or cfg.stock_video_footage_folder
    target_directory.mkdir(parents=True, exist_ok=True)

    stream = (
        YouTube(url)
        .streams.filter(file_extension="mp4", progressive=True)
        .order_by("resolution")
        .desc()
        .first()
    )

    if stream is None:
        raise ValueError("No suitable MP4 stream found for the supplied URL.")

    download_path = Path(
        stream.download(output_path=str(target_directory), filename=filename)
    ).resolve()

    return download_path


__all__ = ["download_video"]
