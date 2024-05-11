number of seconds to convert.
    
    Returns:
    - str: The time in SRT format.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02f}:{minutes:02f}:{seconds:02f},000"

def split_string_into_chunks(text, chunk_size=5):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def get_mp3_length(file_path):
    try:
        audio = MP3(file_path)
        length_in_seconds = audio.info.length
        return length_in_seconds
    except HeaderNotFoundError:
        return None

def count_words(text):
    words = text.split()
    return len(words)

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

def text_to_mp3_gTTS(text: str = '', speed: float = 1) -> str:
    """
    Takes in text and generates an mp3 of the text being read

    Args:
        text: str to be converted
        speed: amount to speed up the audio

    Returns:
        str: Path to mp3 file

    Outputs:
        mp3 file of the post being read
    """

    # Create a string and build it with the cleaned subtexts

    # Get the name of the mp3