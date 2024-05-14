# between 100 - 180 word stories
# write a short adlib generator and then use chatgpt ot flesh out the stories
from openai import OpenAI
import tiktoken
import json

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

gpt_model = config["gpt_model"]


class fill:
    '''
    fills in slots in an adlib
    spot linkes to a tag in a string
    '''
    def __init__(self, spot, data):
        self.TYPE = spot
        self.data = data


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(gpt_model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_GPT_response():
    client = OpenAI()

    completion = client.chat.completions.create(
    model=gpt_model,
    messages=[
        {"role": "system", "content": "You are an average user of Reddit, responding to prompts in your favorite subreddits in slightly unbelievable fashion 100 to 160 words."},
        {"role": "user", "content": "What was the worst experience you have had with healthcare in the United States of America"}
    ]
    )

    if completion.choices[0].message.content is not None:
        print("Request Cost: " + str((num_tokens_from_string("What was the worst experience you have had with healthcare in the United States of America") + num_tokens_from_string(string=completion.choices[0].message.content))) + " Tokens")
        print(completion.choices[0].message.content)


test_text = "@@0! I can't believe it! When I was @@1 my @@2, Someone was watching! I feel so @@3. @@0!"

def count_occurrences(input_str):
    # Find the largest number after a tag
    n = max([int(tag[2]) for tag in input_str.split() if tag.startswith("@@")], default=0)
    
    # Create a list of size n+1 and initialize all counts to 0
    occurrences = [0] * (n + 1)
    
    # Count occurrences of each number
    for tag in input_str.split():
        if tag.startswith("@@"):
            num = int(tag[2])
            occurrences[num] += 1
    
    return occurrences

def fill_slot(text: str, slot: int, words: list):
    # not gonna work!!! think of a recursive solution!!!
    return




def madlib(input_str: str, fill_spots: list):
    '''
        input_str: a string with empty spots (see below)
        fill_spots: an object array of fill objects used to fill the spots in input_str

        an "empty spot" is defined as @@<number> example: (@@1, @@2), 
            which type of word the numbers are is defined by the user
    '''

    # get the number of slots in each category
    occurrences = count_occurrences(input_str)
    print(occurrences)

    # for each category that has over one of each input space
        # permute to make each combination of the input
            # for each permutation, save each one in a new entry in a csv file


madlib(test_text,[])
