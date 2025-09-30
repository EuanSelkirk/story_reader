"""Command-line interface for the story reader application."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, Tuple

from configuration import AppConfig, get_config
import mp4

MENU_DIVIDER = "=" * 60


def _capture_multiline_input() -> str:
    print("Enter the story text. Submit an empty line to finish.")
    lines = []
    while True:
        line = input()
        if line.strip() == "" and lines:
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _prompt_for_text() -> str:
    while True:
        print(
            "\nChoose an input method:\n"
            "  1) Paste the story text\n"
            "  2) Load text from a file\n"
        )
        choice = input("Selection: ").strip()

        if choice == "1":
            text = _capture_multiline_input()
            if text:
                return text
            print("Text cannot be empty. Please try again.")
        elif choice == "2":
            file_path = Path(input("Enter the path to the text file: ").strip())
            if not file_path.is_file():
                print(f"File '{file_path}' does not exist. Please try again.")
                continue
            return file_path.read_text(encoding="utf-8").strip()
        else:
            print("Invalid option. Please choose 1 or 2.")


def _handle_generate_standard(config: AppConfig) -> None:
    text = _prompt_for_text()
    output_path = mp4.generate_video(text, config)
    print(f"\nVideo created successfully at: {output_path}")


def _handle_generate_ai(config: AppConfig) -> None:
    text = _prompt_for_text()
    output_path = mp4.generate_ai_powered_video(text, config)
    print(f"\nAI-powered video created successfully at: {output_path}")


def _handle_show_config(config: AppConfig) -> None:
    print("\nCurrent configuration:")
    for key, value in asdict(config).items():
        print(f"  {key}: {value}")


def _handle_reload_config(_: AppConfig) -> AppConfig:
    print("Reloading configuration from disk...\n")
    return get_config(force_reload=True)


def main() -> None:
    config = get_config()
    actions: Dict[str, Tuple[str, Callable[[AppConfig], AppConfig | None]]] = {
        "1": ("Generate narrated short (gTTS)", lambda cfg: _handle_generate_standard(cfg) or None),
        "2": (
            "Generate narrated short with AI subtitles",
            lambda cfg: _handle_generate_ai(cfg) or None,
        ),
        "3": ("Show configuration", lambda cfg: _handle_show_config(cfg) or None),
        "4": ("Reload configuration", _handle_reload_config),
    }

    while True:
        print("\n" + MENU_DIVIDER)
        print("Story Reader Menu")
        print(MENU_DIVIDER)
        for key, (label, _) in actions.items():
            print(f"{key}) {label}")
        print("q) Quit")

        choice = input("\nSelect an option: ").strip().lower()
        if choice == "q":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please try again.")
            continue

        label, handler = action
        try:
            result = handler(config)
            if isinstance(result, AppConfig):
                config = result
        except Exception as exc:  # noqa: BLE001 - surface errors to the user
            print(f"An error occurred while executing '{label}': {exc}")


if __name__ == "__main__":
    main()
