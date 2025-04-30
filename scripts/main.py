import mp4
import json
# import story_to_AI_story
# import utilities 
import argparse
import os
import sys
import synchron_story_generation as SSG

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

# # Path to your JSONL file
# jsonl_file_path = "/Users/euan/Desktop/story_reader/files/gpt_response_jsonl/batch_e9DN9UAOXD9G4jgO697tRUKY_output.jsonl"

# messages = story_to_AI_story.extract_message_contents(jsonl_file_path)


#utilities.update_parent_folder_path()

# mp4.generate_video(text2)
# for message in messages:
#     mp4.generate_AI_powered_video(message)

# I want to run it so that it takes in a .in file with the format specified
# The program takes the input and...
#     - Generates the permutations of the strings
#     - One by one sends them to chatgpt to get fleshed out
#     - Turns each string into an mp4 
#     - Saves said mp4 somewhere

def main():
    [story_permutations_filepath, name_seed] = SSG.make_stories_from_input_file()

    gpt_response_filepath = SSG.full_story_from_out_OpenAI(story_permutations_filepath, name_seed)
    # gpt_response_filepath = '/Users/euan/Desktop/story_reader/files/gpt_response_stories/20240812164416.txt'

    with open(gpt_response_filepath,'r') as stories:
        for story in stories:
            mp4.generate_AI_powered_video(story.strip())
    


if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process a file as console input.")
    
    # Add a required positional argument for the file path
    parser.add_argument("input_file_path", type=str, help="Path to the input file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Open the file and redirect sys.stdin to read from it
    with open(args.input_file_path, 'r') as file:
        sys.stdin = file
        main()



