"""Video generation helpers."""
from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

from moviepy.editor import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

import audio
import audioAI
from configuration import AppConfig, get_config

CONFIG = get_config()


def _list_video_files(directory: Path) -> Iterable[Path]:
    return [path for path in directory.iterdir() if path.is_file()]


def _choose_video_file(config: AppConfig) -> Path:
    video_files = list(_list_video_files(config.stock_video_footage_folder))
    if not video_files:
        raise FileNotFoundError(
            f"No video files found in {config.stock_video_footage_folder}."
        )
    return random.choice(video_files)


def _build_subtitle_clip(subtitle_path: Path, video_size: Tuple[int, int]) -> SubtitlesClip:
    def generator(text: str) -> TextClip:
        return TextClip(
            text,
            font="DejaVu-Sans",
            fontsize=50,
            color="white",
            method="caption",
            stroke_color="black",
            stroke_width=2,
            size=video_size,
        )

    return SubtitlesClip(str(subtitle_path), generator).set_position("center")


def _write_video(
    video_segment: VideoFileClip,
    audio_clip: AudioFileClip,
    subtitle_path: Path,
    config: AppConfig,
) -> Path:
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    duration = int(audio_clip.duration)
    final_clip_path = config.output_video_folder / f"{duration}_{current_date}.mp4"
    temp_audio_path = config.temp_file_folder / f"{duration}_{current_date}_temp.m4a"

    subtitle_clip = _build_subtitle_clip(subtitle_path, video_segment.size)
    final_clip = CompositeVideoClip([video_segment.set_audio(audio_clip), subtitle_clip])

    try:
        final_clip.write_videofile(
            str(final_clip_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(temp_audio_path),
        )
    finally:
        subtitle_clip.close()
        final_clip.close()
        video_segment.close()
        temp_audio_path.unlink(missing_ok=True)

    return final_clip_path


def generate_video(text: str, config: AppConfig | None = None) -> Path:
    cfg = config or CONFIG
    skeleton_path = audio.text_to_mp3_and_srt_gTTS(text, cfg)
    audio_path = skeleton_path.with_suffix(".mp3")
    subtitle_path = skeleton_path.with_suffix(".srt")

    audio_clip = AudioFileClip(str(audio_path))
    try:
        video_path = _choose_video_file(cfg)
        video_clip = VideoFileClip(str(video_path))
        try:
            if video_clip.duration < audio_clip.duration:
                raise ValueError("Video duration is shorter than the audio duration.")

            start_time = random.uniform(0, video_clip.duration - audio_clip.duration)
            segment = video_clip.subclip(start_time, start_time + audio_clip.duration)
            output_path = _write_video(segment, audio_clip, subtitle_path, cfg)
        finally:
            video_clip.close()
    finally:
        audio_clip.close()
        audio_path.unlink(missing_ok=True)
        subtitle_path.unlink(missing_ok=True)

    return output_path


def generate_ai_powered_video(text: str, config: AppConfig | None = None) -> Path:
    cfg = config or CONFIG
    audio_path = audioAI.get_mp3_from_text(text, cfg)
    subtitle_path = audioAI.generate_srt_from_mp3(audio_path, cfg)

    audio_clip = AudioFileClip(str(audio_path))
    try:
        video_path = _choose_video_file(cfg)
        video_clip = VideoFileClip(str(video_path))
        try:
            if video_clip.duration < audio_clip.duration:
                raise ValueError("Video duration is shorter than the audio duration.")

            start_time = random.uniform(0, video_clip.duration - audio_clip.duration)
            segment = video_clip.subclip(start_time, start_time + audio_clip.duration)
            output_path = _write_video(segment, audio_clip, subtitle_path, cfg)
        finally:
            video_clip.close()
    finally:
        audio_clip.close()
        audio_path.unlink(missing_ok=True)
        subtitle_path.unlink(missing_ok=True)

    return output_path


__all__ = ["generate_video", "generate_ai_powered_video"]
