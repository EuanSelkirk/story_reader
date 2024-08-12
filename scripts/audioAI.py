import os
import json
from datetime import datetime
from faster_whisper import WhisperModel
from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
from openai import OpenAI
import numpy as np

client = OpenAI()

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

model_size = config["model_size"]
temp_file_folder = config["temp_file_folder"]
words_per_line = int(config["words_per_line"])
clip_length_cutoff = int(config["clip_length_cutoff"])
speed = float(config["speed"])
audio_method = config["audio_method"]
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

def get_bit_depth(audio_file):
    audio = AudioSegment.from_file(audio_file)
    
    # Convert audio to numpy array
    samples = np.array(audio.get_array_of_samples())
    
    # Check the maximum value based on bit depth
    max_val = np.max(np.abs(samples))
    if max_val <= 2**8 - 1:
        bit_depth = 8
    elif max_val <= 2**15 - 1:
        bit_depth = 16
    elif max_val <= 2**23 - 1:
        bit_depth = 24
    else:
        bit_depth = 'unknown'
    
    return bit_depth

def remove_clipping(audio_file):
    # Load audio file
    audio = AudioSegment.from_file(audio_file)
    
    # Convert audio to numpy array
    samples = np.array(audio.get_array_of_samples())
    
    # Determine the bit depth
    bit_depth = get_bit_depth(audio_file)
    
    # Set max_amplitude based on bit depth
    if bit_depth == 8:
        max_amplitude = 2**7 - 1  # for 8-bit audio
    elif bit_depth == 16:
        max_amplitude = 2**15 - 1  # for 16-bit audio
    elif bit_depth == 24:
        max_amplitude = 2**23 - 1  # for 24-bit audio
    else:
        max_amplitude = 2**15 - 1  # Default to 16-bit if unknown
    
    # Check for clipping
    clipped = np.any(np.abs(samples) >= max_amplitude)
    
    if not clipped:
        print("No clipping detected.")
        return
    
    # Normalize audio
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        normalize_factor = max_amplitude / max_val
        samples = (samples * normalize_factor).astype(np.int16)
    
    # Convert back to AudioSegment
    audio = audio._spawn(samples.tobytes())
    
    # Export the fixed audio, overwriting the original file
    audio.export(audio_file, format="mp3")
    print(f"Audio fixed and saved to {audio_file}")

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

from pydub import AudioSegment

def get_mp3_openAI_from_text(text: str = '') -> str:
    # get the path to the chunk
    audio_path = f'{temp_file_folder}{name_seed}.mp3'

    print("Generating audio...", temp_file_folder)

    match audio_method:
        case 'OpenAI':
            # generate the audio for the chunk
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )

            # save the chunk at the tmp path
            response.stream_to_file(audio_path)
        case _:
            # generate the audio for the chunk
            audio = gTTS(text, lang='en', slow=False)

            # save the chunk at the tmp path
            audio.save(audio_path)

    # remove_clipping(audio_path)

    print("Audio generated! Checking duration...")

    # Load the audio file to check its duration
    audio = AudioSegment.from_mp3(audio_path)
    duration_in_seconds = len(audio) / 1000  # pydub returns duration in milliseconds

    # If the audio is longer than 59 seconds, speed it up
    if duration_in_seconds > 59:
        print(f"Audio is {duration_in_seconds:.2f} seconds long. Speeding it up to fit within 59 seconds.")
        speed_factor = duration_in_seconds / 59
        sped_up_audio = audio.speedup(playback_speed=speed_factor)
        sped_up_audio.export(audio_path, format="mp3")
        print("Audio sped up!")

    return audio_path


def generate_srt_from_mp3(audio_file_path: str = ''):
    print("Generating srt...")
    model = WhisperModel(model_size)
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
