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



