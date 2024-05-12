import os
import io
import json
import string
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)



temp_file_folder = config["temp_file_folder"]
words_per_line = int(config["words_per_line"])
clip_length_cutoff = int(config["clip_length_cutoff"])
speed = float(config["speed"])

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

def split_string_into_length_n(text, n):
    """
    Split a string into an array of strings where the strings are length n.
    
    Args:
    - text (str): The string to split.
    - n (int): The length of the strings.
    
    Returns:
    - str[]: Array of strings.
    """
    return [text[i:i+n] for i in range(0, len(text), n)]

def split_string_into_sentences(text):
    """
    Split a string into an array of sentences.
    
    Args:
    - text (str): The string to split.
    
    Returns:
    - str[]: Array of sentences.
    """
    sentences = []
    words = text.split()
    current_sentence = []
    for word in words:
        current_sentence.append(word)
        for char in word:
            if char != ',' and char in string.punctuation:
                sentences.append(current_sentence)
                current_sentence = []

    return sentences

def get_mp3_length_saved(file_path):
    """
    Get the length in seconds of a mp3 file.
    
    Args:
    - file_path (str): The path to the mp3 file.
    
    Returns:
    - int: Time in seconds.
    """
    length_in_seconds = 0.0
    try:
        audio = MP3(file_path)
        length_in_seconds = audio.info.length
        return length_in_seconds
    except HeaderNotFoundError:
        return None

def count_words(text):
    """
    Get the length in words of a string.
    
    Args:
    - text (str): The text.
    
    Returns:
    - int: Number of words.
    """
    words = text.split()
    return len(words)

def get_last_word(text):
    """
    Get the last word in a string
    
    Args:
    - text (str): The text.
    
    Returns:
    - str: The last word.
    """
    words = text.split()
    if words:
        return words[-1]
    else:
        return None

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
        raise RuntimeError(f"An error occurred while processing the audio: {str(e)}")

def text_to_mp3_and_srt_gTTS(text: str = '') -> str:
    """
    Takes in text and generates an mp3 and srt of the text being read

    Args:
        text: str to be converted

    Returns:
        str: Skeleton path to the mp3 and srt files
             (Need to add .mp3 and .srt to the end)

    Outputs:
        mp3 file of the post being read
        srt file containing the timed subtitles
    """

    # get the seed for the name of the tmp files
    name_seed = datetime.now().strftime("%Y%m%d%H%M%S")

    # take the text and split it into m chunks of n length in words
    chunks = split_string_into_sentences(text)

    # modify the chunks for audio processing
    audioChunks = [" ".join(inner_array) for inner_array in chunks]

    # modify the chunks for subtitle processing
    textChunks = [[' '.join(chunk) for chunk in split_string_into_length_n(sentence, words_per_line)] for sentence in chunks]

    # for each audio chunk
    for i, chunk in enumerate(audioChunks):
        # get the path to the chunk
        audio_path = f'{temp_file_folder}{i}_{name_seed}.mp3'

        # generate the audio for the chunk
        audio = gTTS(chunk, lang='en', slow=False)

        # save the chunk at the tmp path
        audio.save(audio_path)

        # modify the audio chunk to include the time and path of the audio
        audioChunks[i] = [chunk, get_mp3_length_saved(audio_path), audio_path]

    # declare and init needed values
    srt_text = ''
    count = 1
    start = end = 0.0

    # using the audio objects, generate the srt filetext
    for i, sentence in enumerate(audioChunks):
        # get the number of text chunks in the current audio chunk
        num_chunks = len(textChunks[i])

        # get the time per text chunk
        time_per_chunk = sentence[1] / num_chunks

        # for each chunk in the text chunks
        for chunk in textChunks[i]:
            # include the count
            srt_text += f'{count}\n'
            count += 1

            # set the end of the time
            end = start + time_per_chunk

            # include the start and end time of the subtitle
            srt_text += f'{convert_to_srt_time(start)} --> {convert_to_srt_time(end)}\n'

            # include the text of the chunk
            srt_text += f'{chunk}\n\n'

            # set up start for next iteration
            start = end

    # set the final audio and srt paths
    final_audio_path = f'{temp_file_folder}{name_seed}.mp3'
    srt_path = f'{temp_file_folder}{name_seed}.srt'

    # get the audio segments from the audio chunks
    audio_segments = [AudioSegment.from_file(audio[2], 'mp3') for audio in audioChunks]

    # concatenate the audio chunks into one audio file and save it at the path
    sum(audio_segments).export(final_audio_path, format="mp3")

    # save the srt file at the path
    with open(srt_path, "w") as f:
        f.write(srt_text)

    # delete any temp files
    for file_path in [audio[2] for audio in audioChunks]:
        os.remove(file_path)

    # return the skeleton of the final file path
    return f'{temp_file_folder}{name_seed}'


# take a string of text and create an audio file of the text being read, as well as a file containing the subtitles
#   split the text into a list of m strings of n length and return the filepath to the audio for each string, 
#       along with the length in ms of the audio file
#   stitch the audios together to form one long audio
#   generate the subtitles by making the strs in the list be however long the corresponding audio is 

# DONE^^^

# Still need to implement the speed up function, and refactor the code to be more modular and use a config file
