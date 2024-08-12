import os
import json
from pytube import YouTube

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

#yt-dlp -f 'bestvideo' -o '/Users/euan/Desktop/story_reader/files/stock_video_footage/%(title)s.%(ext)s' 'https://www.youtube.com/watch?v=z121mUPexGc'



def update_parent_folder_path():
    # Get the current directory of the current Python script
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(current_directory)

    json_directory = current_directory + "/config/config.json"

    # Read the JSON file
    with open(json_directory, 'r') as file:
        config = json.load(file)

    # Update the parent_folder variable
    config['parent_file_folder'] = current_directory

    # Write the updated JSON back to the file
    with open(json_directory, 'w') as file:
        json.dump(config, file, indent=4)

#print(downloadVideo('https://www.youtube.com/watch?v=u7kdVe8q5zs&t=210s', stock_video_footage_folder_uncropped))
