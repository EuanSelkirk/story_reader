from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from gtts import gTTS
from mutagen.mp3 import HeaderNotFoundError, MP3
from pydub import AudioSegment

from configuration import AppConfig, get_config

CONFIG = get_config()

def convert_to_srt_time(seconds: float) -> str:
    """Convert seconds to SubRip (.srt) time format."""

    milliseconds = int(round(seconds * 1000))
    remaining_milliseconds = milliseconds % 1000
    seconds_total = milliseconds // 1000
    minutes, seconds_only = divmod(seconds_total, 60)
    hours, minutes_only = divmod(minutes, 60)
    return f"{hours:02d}:{minutes_only:02d}:{seconds_only:02d},{remaining_milliseconds:03d}"


def chunk_words(words: Iterable[str], chunk_size: int) -> List[str]:
    """Split words into evenly sized chunks."""

    word_list = list(words)
    return [" ".join(word_list[i : i + chunk_size]) for i in range(0, len(word_list), chunk_size)]


def split_string_into_sentences(text: str) -> List[List[str]]:
    """Split text into sentences represented as word lists."""

    normalized_text = " ".join(text.strip().split())
    if not normalized_text:
        return []

    sentence_terminators = {".", "!", "?", ";", ":"}
    sentences: List[List[str]] = []
    current_sentence: List[str] = []

    for word in normalized_text.split(" "):
        current_sentence.append(word)
        if word[-1] in sentence_terminators:
            sentences.append(current_sentence)
            current_sentence = []

    if current_sentence:
        sentences.append(current_sentence)

    return sentences

def get_mp3_length_saved(file_path: Path) -> float:
    """Return the length of an MP3 file in seconds."""

    try:
        audio = MP3(str(file_path))
        return float(audio.info.length)
    except HeaderNotFoundError as exc:
        raise ValueError(f"Unable to read MP3 header for {file_path}.") from exc

def speed_up_audio(input_file: Path, output_file: Path, speed_factor: float) -> None:
    """Speed up the audio at ``input_file`` and write it to ``output_file``."""

    # Check if input file exists
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    try:
        # Load audio from input file
        audio = AudioSegment.from_mp3(str(input_file))

        # Check if the speed factor is valid
        if speed_factor <= 0:
            raise ValueError("Speed factor must be a positive value.")

        # Speed up the audio
        modified_audio = audio.speedup(playback_speed=speed_factor)

        # Export the modified audio to the output file
        modified_audio.export(str(output_file), format="mp3")

    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the audio: {str(e)}") from e

def text_to_mp3_and_srt_gTTS(text: str, config: AppConfig | None = None) -> Path:
    """Generate MP3 audio and subtitles for the supplied text."""

    cfg = config or CONFIG
    if not text.strip():
        raise ValueError("Text must not be empty.")

    name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
    sentence_chunks = split_string_into_sentences(text)

    if not sentence_chunks:
        raise ValueError("Unable to derive sentences from text input.")

    subtitle_chunks = [
        chunk_words(sentence, cfg.words_per_line) for sentence in sentence_chunks
    ]

    audio_chunks: List[tuple[str, float, Path]] = []
    for index, words in enumerate(sentence_chunks):
        chunk_text = " ".join(words)
        chunk_path = cfg.temp_file_folder / f"{index}_{name_seed}.mp3"
        tts = gTTS(chunk_text, lang="en", slow=False)
        tts.save(str(chunk_path))
        audio_chunks.append((chunk_text, get_mp3_length_saved(chunk_path), chunk_path))

    srt_lines = []
    counter = 1
    start = 0.0

    for chunk_index, chunk in enumerate(audio_chunks):
        chunk_text, chunk_duration, _ = chunk
        text_chunks = subtitle_chunks[chunk_index] or [chunk_text]
        time_per_chunk = chunk_duration / max(len(text_chunks), 1)

        for text_chunk in text_chunks:
            end = start + time_per_chunk
            srt_lines.append(str(counter))
            srt_lines.append(
                f"{convert_to_srt_time(start)} --> {convert_to_srt_time(end)}"
            )
            srt_lines.append(text_chunk)
            srt_lines.append("")
            counter += 1
            start = end

    final_audio_path = cfg.temp_file_folder / f"{name_seed}.mp3"
    final_srt_path = cfg.temp_file_folder / f"{name_seed}.srt"

    combined_audio = AudioSegment.empty()
    for _, _, chunk_path in audio_chunks:
        combined_audio += AudioSegment.from_file(str(chunk_path), "mp3")
    combined_audio.export(str(final_audio_path), format="mp3")

    final_srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    for _, _, chunk_path in audio_chunks:
        chunk_path.unlink(missing_ok=True)

    return final_audio_path.with_suffix("")
