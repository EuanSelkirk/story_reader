import os
import json


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
