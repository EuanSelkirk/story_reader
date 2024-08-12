import audioAI
import json
import os
import random
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.io.VideoFileClip import AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from datetime import datetime

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

temp_file_folder = config["temp_file_folder"]
output_video_folder = config["output_video_folder"]
stock_video_footage_folder = config["stock_video_footage_folder"]
y_position_divisor = int(config["y_position_divisor"])

font_path = config['subtitle_font']

def generate_AI_powered_video(text: str = ''):
    try:
        # generate mp3 and srt files and get the path to them
        audio_file_path = audioAI.get_mp3_openAI_from_text(text=text)

        # get the audio clip
        audio_clip = AudioFileClip(audio_file_path)

        short_duration = audio_clip.duration

        # get the list of video clips
        video_extensions = ['.mp4']  # Add more extensions if needed
        videoFootageFiles = [f for f in os.listdir(stock_video_footage_folder) if os.path.splitext(f)[1] in video_extensions]

        # in case there are no video clips
        if not videoFootageFiles:
            raise ValueError("No video files found in the stock video footage folder.")

        # get a random video file
        random_stock_footage_file = random.choice(videoFootageFiles)

        video_clip_path = os.path.join(stock_video_footage_folder, random_stock_footage_file)

        # if the video file path was not created
        if not os.path.isfile(video_clip_path):
            raise FileNotFoundError(f"Video file '{video_clip_path}' not found.")

        video_clip = VideoFileClip(video_clip_path)

        video_duration = video_clip.duration

        # filter out very long audio or very short videos
        if video_duration < short_duration:
            raise ValueError("Video duration is shorter than the audio duration.")

        # get the start time for the short
        start_time = random.uniform(0, video_duration - short_duration)

        # get the short clip based on the audio length
        segment_clip = video_clip.subclip(start_time, start_time + short_duration).set_audio(audio_clip)

        # generate the subttles and get the path to them
        subtitle_file_path = audioAI.generate_srt_from_mp3(audio_file_path=audio_file_path)

        # switch object to get the text scaling based on the video resolution
        switch_fontsize = {
            2160: 125,
            1440: 100,
            1080: 75,
            720: 50
        }

        fontsize = switch_fontsize.get(video_clip.size[1], 720)

        # Calculate Y position between center and bottom
        custom_y = (video_clip.size[1] // y_position_divisor)

        # define the generator for the subtitle text
        generator = lambda txt: TextClip(txt, font=font_path, fontsize=fontsize, color="white", method='caption', size=segment_clip.size, stroke_color='black')

        # create and position the subtitles
        subtitle_clip = SubtitlesClip(subtitle_file_path, generator).set_position(('center', custom_y))

        # put the video and subtitles together
        final_clip = CompositeVideoClip([segment_clip, subtitle_clip])

        current_date = datetime.now().strftime('%Y%m%d%H%M%S')

        final_clip_path = os.path.join(output_video_folder, f'{int(short_duration)}_{current_date}.mp4')

        temp_video_path = os.path.join(temp_file_folder, f'{int(short_duration)}_{current_date}.mp4')

        # save final video clip
        final_clip.write_videofile(final_clip_path, codec='libx264', audio_codec='aac', threads = 4, temp_audiofile=temp_video_path)

        # remove temp files
        os.remove(audio_file_path)
        os.remove(subtitle_file_path)

        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
