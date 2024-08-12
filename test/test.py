# from openai import OpenAI
# client = OpenAI()

# completion = client.chat.completions.create(
#   model="gpt-4o-mini",
#   messages=[
#     {"role": "system", "content": "You are to take stories given to you and rewrite them in a reddit style, skipping any intro and audience questions, only telling the juicy story!"},
#     {"role": "user", "content": "One time when I went to the store to buy popcorn, it got robbed and I escaped without harm."},
#     {"role": "user", "content": "One time when I went to the movies to buy popcorn, it was robbed and I was trapped."}
#   ]
# )

# print(completion.choices[0].message)
# print(completion.choices[1].message)

from TTS.api import TTS

# Initialize the TTS with your desired model
tts = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=False, gpu=False)

# Define the text you want to convert to speech
text = "I was working late at the office one night, running some routine checks on our old MAINFRAME system. You know, the type of machine that feels like it's held together with duct tape and wishes. Everything seemed fine until I accidentally triggered a system test that I had no idea would be this intense.\n\nSuddenly lights started flashing, alarms blaring, and the room felt like it was about to go into meltdown mode. Panic set in as I scrambled to figure out how to halt this chaos. In my haze, I accidentally hit the wrong buttons, causing the mainframe to go into overdrive. The monitors were displaying error codes I'd never seen before, like a horror movie glitching out.\n\nTrying to calm myself, I remembered the emergency protocol. I raced to the console, but it was like fighting a sentient beast. It was as if the mainframe knew I was flailing and decided to put on a dramatic show just to mess with me. Data started flashing on the screen at lightning speed\u2014gibberish mixed with real-time analytics that I had to decipher in a rush.\n\nJust when I thought I couldn't take any more stress, the MAINFRAME suddenly rebooted and everything went black\u2014dead silence. My heart raced. Had I broken it? As I sat there in darkness, I realized the universe had decided to teach me a lesson about respect for ancient technology.\n\nFinally, the machine whirred back to life, but this time with the sweetest hum of stability. Everything was back to normal as if the chaos never happened. I sat back in my chair, shaky and sweating, but relieved. Lesson learned: handle the MAINFRAME with care, or it might just throw a fit."

# Define the output path
output_path = "output.wav"

# Convert text to speech and save it as a WAV file
tts.tts_to_file(text=text, file_path=output_path)

print(f"Speech saved to {output_path}")
