import re as regex
from datetime import datetime
import json
from collections import defaultdict

# To use:
#     - Either follow the prompts in the console or
#       make a txt file with the following format
#       - Skeleton str
#         [category]
#         words in category
#         repeat until all categories covered
#     - run with the <"filename" in the console

with open('/Users/euan/Desktop/story_reader/config/config.json', 'r') as f:
    config = json.load(f)

generated_stories_filepath = config[ "generated_story_path"]
name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
output_path = f'{generated_stories_filepath}/{name_seed}.out'

class Word:
    def __init__(self, str, category):
        self.str = str
        self.category = category
        self.used = False

    def __str__(self):
        return f"{self.str}"

    def __repr__(self):
        return self.__str__()

# Open file for writing the results
file_out = open(output_path, "w")

# Read the skeleton string
skeleton_str = input("Enter the skeleton string: ")

# Regular expression to find words inside square brackets
pattern = r"\[([^\]]+)\]"

# Find all matches
matches = regex.findall(pattern, skeleton_str)

# Get the array of placeholders
placeholders = [match for match in matches]

print("Placeholders found:", placeholders)

# Dictionary to store the count of each category
category_count = defaultdict()

# Update the count for each category found
for match in matches:
    category_count[match] += 1

# Print the sorted list of categories and ask user for input
user_input = {}
while len(user_input) < len(category_count):
    try:
        user_category = input("Please enter the category name [in brackets]: ").strip("[]")
        if user_category in category_count and user_category not in user_input:
            count = category_count[user_category]
            user_words = input(f"Please enter at least {count} words for the category '{user_category}' (separated by spaces): ").split()
            if len(user_words) >= count:
                user_input[user_category] = [Word(word, user_category) for word in user_words]
            else:
                print(f"Please enter at least {count} words.")
        else:
            print("Invalid category or category already entered.")
    except ValueError:
        print("Invalid input. Please try again.")

max_spaces = len(placeholders)
str_matches_permutations = []

def generate_permutations(space, curr_build):
    if space >= max_spaces:
        # Join the current build into a string and store it
        final_str = skeleton_str
        for i, word in enumerate(curr_build):
            final_str = final_str.replace(f"[{placeholders[i]}]", word.str, 1)
        str_matches_permutations.append(final_str)
        return

    curr_category = placeholders[space]
    curr_words = user_input[curr_category]

    for word in curr_words:
        if not word.used:
            word.used = True
            curr_build[space] = word
            generate_permutations(space + 1, curr_build)
            word.used = False

generate_permutations(0, [None] * max_spaces)

# Print the results
for permutation in str_matches_permutations:
    file_out.write(f"{permutation}\n")

# Update the key with the new file path
config["recent_stories_generated"] = output_path

# Write the updated settings back to the JSON file
with open('/Users/euan/Desktop/story_reader/config/config.json', "w") as file:
    json.dump(config, file, indent=4)

file_out.close()

from openai import OpenAI
import json
from datetime import datetime
import time

client = OpenAI()

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

generated_story_path = config["recent_stories_generated"]
gpt_model = config["gpt_model"]
assistant_instructions = config["assistant_instructions"]
jsonl_story_path = config["jsonl_story_path"]
name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
output_path = f"{jsonl_story_path}/{name_seed}.jsonl"

def generated_stories_to_jsonl():
    output_file = open(output_path, "w")
    count = 1
    with open(generated_story_path, 'r') as stories:
        for story in stories:
            output_file.write("{\"custom_id\": \"request-" + str(count) + "\", \"method\": \"POST\", \"url\": \"/v1/chat/completions\", \"body\": {\"model\": \"" + gpt_model + "\", \"messages\": [{\"role\": \"system\", \"content\": \"" + assistant_instructions + "\"},{\"role\": \"user\", \"content\": \"" + story.strip() + "\"}]}}")
            output_file.write("\n")
            count += 1
    output_file.close()

# Path to your JSONL file
jsonl_file_path = "/Users/euan/Desktop/story_reader/files/gpt_response_jsonl/batch_e9DN9UAOXD9G4jgO697tRUKY_output.jsonl"

def extract_message_contents(jsonl_file_path):
    message_contents = []

    with open(jsonl_file_path, 'r') as file:
        for line in file:
            # Parse each line as a JSON object
            entry = json.loads(line.strip())
            
            # Check if the response, body, and choices fields exist
            if 'response' in entry and 'body' in entry['response']:
                body = entry['response']['body']
                
                # Check if choices field exists and has the message content
                if 'choices' in body and len(body['choices']) > 0:
                    message = body['choices'][0].get('message', {})
                    content = message.get('content')
                    
                    if content:
                        message_contents.append(content)

    return message_contents

# Call the function and store the extracted message contents
message_contents = extract_message_contents(jsonl_file_path)

# Print the extracted message contents
for body in message_contents:
    print(body)



