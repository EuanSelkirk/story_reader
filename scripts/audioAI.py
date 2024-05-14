import os
import json
from datetime import datetime
from faster_whisper import WhisperModel
from gtts import gTTS
from pydub import AudioSegment


with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

model_size = config["model_size"]
temp_file_folder = config["temp_file_folder"]
words_per_line = int(config["words_per_line"])
clip_length_cutoff = int(config["clip_length_cutoff"])
speed = float(config["speed"])

model = WhisperModel(model_size)
name_seed = datetime.now().strftime("%Y%m%d%H%M%S")

def convert_to_srt_time(seconds: float):
    """
    Convert seconds to SubRip (.srt) time format (hh:mm:ss,sss).

    Args:
    - seconds (float): The number of seconds to convert.

    Returns:
    - str: The time in SRT format.
    """

    milliseconds = int(seconds * 1000)
    seconds = int(seconds)

    return f"{0:02d}:{0:02d}:{seconds:02d},{(milliseconds - (seconds*1000)):03d}"


def speed_up_audio(input_file: str, output_file: str, speed_factor: float):
    """
    Speeds up the audio in an mp3 file

    Args:
        input_file (str): Input file path
        output_file (str): Output file path
        speed_factor (float): Factor to speed up the mp3 file with
    """

    # Check if input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    try:
        # Load audio from input file
        audio = AudioSegment.from_mp3(input_file)

        # Check if the speed factor is valid
        if speed_factor <= 0:
            raise ValueError("Speed factor must be a positive value.")

        # Speed up the audio
        modified_audio = audio.speedup(playback_speed=speed_factor)

        # Export the modified audio to the output file
        modified_audio.export(output_file, format='mp3')

    except Exception as e:
        raise RuntimeError(
            f"An error occurred while processing the audio: {str(e)}")

def get_mp3_from_text(text: str = '') -> str:
    # get the path to the chunk
    audio_path = f'{temp_file_folder}{name_seed}.mp3'

    print("Generating audio...", temp_file_folder)

    # generate the audio for the chunk
    audio = gTTS(text, lang='en', slow=False)

    # save the chunk at the tmp path
    audio.save(audio_path)

    print("Audio generated! Speeding up Audio...")

    if(speed != 1):
        speed_up_audio(audio_path, audio_path, speed)

    print("Audio sped up!")

    return audio_path

def generate_srt_from_mp3(audio_file_path: str = ''):
    print("Generating srt...")
    segments, info = model.transcribe(audio_file_path, word_timestamps=True)
    segments = list(segments)
    srt = ''

    for segment in segments:
        if segment.words is not None:  # Check if words attribute is not None
            for i, word in enumerate(segment.words):
                srt += f'{i+1}\n'
                srt += f'{convert_to_srt_time(word.start)} --> {convert_to_srt_time(word.end)}\n'
                srt += f'{word.word.strip()}\n\n'

    srt_path = f'{temp_file_folder}{name_seed}.srt'

    # save the srt file at the path
    with open(srt_path, "w") as f:
        f.write(srt)

    print("Srt generated!")

    return srt_path
