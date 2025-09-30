from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
from gtts import gTTS

from configuration import AppConfig, get_config
from audio import speed_up_audio

CONFIG = get_config()
_MODEL: Optional[WhisperModel] = None

def _get_model(config: AppConfig) -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel(config.model_size)
    return _MODEL


def convert_to_srt_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    remaining_milliseconds = milliseconds % 1000
    seconds_total = milliseconds // 1000
    minutes, seconds_only = divmod(seconds_total, 60)
    hours, minutes_only = divmod(minutes, 60)
    return f"{hours:02d}:{minutes_only:02d}:{seconds_only:02d},{remaining_milliseconds:03d}"


def get_mp3_from_text(text: str, config: AppConfig | None = None) -> Path:
    cfg = config or CONFIG
    if not text.strip():
        raise ValueError("Text must not be empty.")

    name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
    audio_path = cfg.temp_file_folder / f"{name_seed}.mp3"
    tts = gTTS(text, lang="en", slow=False)
    tts.save(str(audio_path))

    if cfg.speed != 1:
        speed_up_audio(audio_path, audio_path, cfg.speed)

    return audio_path


def generate_srt_from_mp3(
    audio_file_path: Path, config: AppConfig | None = None
) -> Path:
    cfg = config or CONFIG
    model = _get_model(cfg)

    segments, _ = model.transcribe(str(audio_file_path), word_timestamps=True)
    srt_lines = []
    counter = 1

    for segment in segments:
        for word in segment.words:
            srt_lines.append(str(counter))
            srt_lines.append(
                f"{convert_to_srt_time(word.start)} --> {convert_to_srt_time(word.end)}"
            )
            srt_lines.append(word.word.strip())
            srt_lines.append("")
            counter += 1

    name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
    srt_path = cfg.temp_file_folder / f"{name_seed}.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    return srt_path
