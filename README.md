# Story Reader

Story Reader is a command-line tool that transforms written stories into engaging vertical videos. It combines automated narration, subtitles, and stock footage to produce short-form videos that are ready to publish.

## Features

- **Configurable pipeline** – Centralised JSON configuration makes it easy to adapt file paths, narration speed, and Whisper model size.
- **Two narration modes** – Generate narration with Google Text-to-Speech or leverage Whisper for AI-generated subtitles.
- **Reusable stock footage** – Randomly selects background clips from a stock footage directory and trims them to match narration length.
- **CLI workflow** – Interactive menu for generating videos, reloading configuration, and inspecting settings.

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) installed and available on your `PATH`
- Ability to install Python packages from `pip`
- (Optional) GPU support for faster Whisper inference when using the AI-powered workflow

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd story_reader
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (if not already installed). On macOS with Homebrew:
   ```bash
   brew install ffmpeg
   ```
   On Ubuntu/Debian:
   ```bash
   sudo apt-get update && sudo apt-get install ffmpeg
   ```

## Configuration

All runtime settings are stored in `config/config.json`. Paths can be absolute or relative to the repository root. By default, generated assets are written to the directories under `files/`.

```json
{
  "temp_file_folder": "files/tmp",
  "output_video_folder": "files/finished_shorts",
  "stock_video_footage_folder": "files/stock_video_916",
  "words_per_line": 5,
  "speed": 1.2,
  "model_size": "medium",
  "clip_length_cutoff": 400
}
```

- `temp_file_folder` – Temporary working directory for intermediate audio/subtitle files.
- `output_video_folder` – Final rendered videos are saved here.
- `stock_video_footage_folder` – Source directory for vertical background footage.
- `words_per_line` – Subtitle wrapping length.
- `speed` – Playback speed multiplier for generated narration.
- `model_size` – Whisper model used for AI subtitle generation (e.g., `base`, `medium`, `large-v2`).
- `clip_length_cutoff` – Maximum clip length (currently used for future extensibility).

Ensure the directories referenced above exist. They will be created automatically the first time the application loads, but you can populate `stock_video_footage_folder` with your own MP4 clips ahead of time.

## Usage

Run the CLI from the project root:

```bash
python scripts/main.py
```

From the menu you can:

1. Generate a narrated short using Google Text-to-Speech.
2. Generate a narrated short with AI-generated subtitles.
3. Inspect the current configuration.
4. Reload configuration changes without restarting the CLI.

When generating a video, you can paste story text directly into the terminal or load it from a file on disk. The resulting MP4 will be saved to the configured output directory.

## Downloading Stock Footage

Use the helper in `scripts/utilities.py` to download footage via Python:

```python
from utilities import download_video

download_video("https://www.youtube.com/watch?v=example")
```

Alternatively, place your own vertical video clips inside the `files/stock_video_916` directory.

## Troubleshooting

- **MoviePy complains about missing codecs** – Ensure FFmpeg is correctly installed and accessible.
- **Whisper model downloads are slow** – Consider selecting a smaller model size in the configuration if you do not have GPU acceleration.
- **No stock footage found** – Populate the `stock_video_footage_folder` with MP4 files before running the generator.

## License

This project is provided as-is to demonstrate a video generation workflow. Adapt it to your needs when preparing job applications or portfolios.
