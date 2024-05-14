import os
import json
from pytube import YouTube

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

stock_video_footage_folder_uncropped = config["stock_video_footage_folder_uncropped"]

def downloadVideo(youtube_link, download_path):
    print("Downloading Video...")
    video = YouTube(youtube_link)
    print('Video Downloaded!')
    print('Saving: ' + video.title)
    video.streams.filter(res='1080p').first().download()

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
