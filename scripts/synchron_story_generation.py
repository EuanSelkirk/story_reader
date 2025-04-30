import re as regex
import json
from datetime import datetime
from collections import defaultdict
from openai import OpenAI
import tiktoken

config_path = '/Users/euan/Desktop/story_reader/config/config.json'

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config_path, config):
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

config = load_config(config_path)

# To use:
#     - Either follow the prompts in the console or
#       make a txt file with the following format
#       - Skeleton str
#         [category]
#         words in category
#         repeat until all categories covered
#     - run with the <"filename" in the console

class Word:
    def __init__(self, str, category):
        self.str = str
        self.category = category
        self.used = False

    def __str__(self):
        return f"{self.str}"

    def __repr__(self):
        return self.__str__()

def generate_permutations(space, max_spaces, placeholders, skeleton_str, user_input, curr_build, str_matches_permutations):
    if space >= max_spaces:
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
            generate_permutations(space + 1, max_spaces, placeholders, skeleton_str, user_input, curr_build, str_matches_permutations)
            word.used = False

def make_stories_from_input_file():
    generated_stories_filepath = config["generated_story_path"]
    name_seed = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = f'{generated_stories_filepath}/{name_seed}.out'

    # Open file for writing the results
    file_out = open(output_path, "w")

    # Read the skeleton string
    skeleton_str = input()

    # Regular expression to find words inside square brackets
    pattern = r"\[([^\]]+)\]"

    # Find all matches
    matches = regex.findall(pattern, skeleton_str)

    # Get the array of placeholders
    placeholders = [match for match in matches]

    # Dictionary to store the count of each category
    category_count = defaultdict(int)

    # Update the count for each category found
    for match in matches:
        category_count[match] += 1

    # Print the sorted list of categories and ask user for input
    user_input = {}
    while len(user_input) < len(category_count):
        try:
            user_category = input().strip("[]")
            if user_category in category_count and user_category not in user_input:
                count = category_count[user_category]
                # Split the input by commas and remove any leading/trailing whitespace from each word/phrase
                user_words = [word.strip() for word in input().split(",")]
                if len(user_words) >= count:
                    user_input[user_category] = [Word(word, user_category) for word in user_words]
                else:
                    print(f"Please enter at least {count} words or phrases.")
            else:
                print("Invalid category or category already entered.")
        except ValueError:
            print("Invalid input. Please try again.")

    
    max_spaces = len(placeholders)

    str_matches_permutations = []

    generate_permutations(0, max_spaces, placeholders, skeleton_str, user_input, [None] * max_spaces, str_matches_permutations)

    # Print the results
    for permutation in str_matches_permutations:
        file_out.write(f"{permutation}\n")

    file_out.close()

    return output_path, name_seed

def full_story_from_out_OpenAI(permuted_stories_filepath, name_seed):
    client = OpenAI()
    encoding = tiktoken.get_encoding("cl100k_base")


    assistant_instructions = config["assistant_instructions"]
    gpt_response_folder = config["gpt_response_stories"]
    gpt_response_filepath = f"{gpt_response_folder}/{name_seed}.txt"
    max_tokens = config["max_tokens"]

    out = open(gpt_response_filepath, 'w')

    with open(permuted_stories_filepath, 'r') as stories:
        for story in stories:
            completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"{assistant_instructions}"},
                {"role": "user", "content": f"{story}"}
            ],
            max_tokens = max_tokens
            )

            if completion.choices[0].message.content:
                out.write(completion.choices[0].message.content.replace('\n', ''))
                out.write('\n')
            else:
                print("Error from gpt response")
        
    out.close()

    return gpt_response_filepath



# _____________________________________________



# def generated_stories_to_jsonl():
#     output_file = open(output_path, "w")
#     count = 1
#     with open(generated_story_path, 'r') as stories:
#         for story in stories:
#             output_file.write("{\"custom_id\": \"request-" + str(count) + "\", \"method\": \"POST\", \"url\": \"/v1/chat/completions\", \"body\": {\"model\": \"" + gpt_model + "\", \"messages\": [{\"role\": \"system\", \"content\": \"" + assistant_instructions + "\"},{\"role\": \"user\", \"content\": \"" + story.strip() + "\"}]}}")
#             output_file.write("\n")
#             count += 1
#     output_file.close()

# def extract_message_contents(jsonl_file_path):
#     message_contents = []

#     with open(jsonl_file_path, 'r') as file:
#         for line in file:
#             # Parse each line as a JSON object
#             entry = json.loads(line.strip())
            
#             # Check if the response, body, and choices fields exist
#             if 'response' in entry and 'body' in entry['response']:
#                 body = entry['response']['body']
                
#                 # Check if choices field exists and has the message content
#                 if 'choices' in body and len(body['choices']) > 0:
#                     message = body['choices'][0].get('message', {})
#                     content = message.get('content')
                    
#                     if content:
#                         message_contents.append(content)

#     return message_contents

# # Call the function and store the extracted message contents
# message_contents = extract_message_contents(jsonl_file_path)

# # Print the extracted message contents
# for body in message_contents:
#     print(body)



