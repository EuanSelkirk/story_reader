import audio
import audioAI
import json
import os
import random
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.io.VideoFileClip import AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from datetime import datetime

with open('/Users/euan/Desktop/story_reader/config/config.json') as f:
    config = json.load(f)

temp_file_folder = config["temp_file_folder"]
output_video_folder = config["output_video_folder"]
stock_video_footage_folder = config["stock_video_footage_folder"]

def generate_video(text: str = '') -> bool:
    try:
        # generate mp3 and srt files and get the path to them
        skeletonFilePath = audio.text_to_mp3_and_srt_gTTS(text=text)

        # get the audio clip
        audio_clip = AudioFileClip(f'{skeletonFilePath}.mp3')

        subtitle_clip = SubtitlesClip(f'{skeletonFilePath}.srt').set_position(('center'))

        short_duration = audio_clip.duration

        videoFootageFiles = os.listdir(stock_video_footage_folder)

        if not videoFootageFiles:
            raise ValueError("No video files found in the stock video footage folder.")

        random_stock_footage_file = random.choice(videoFootageFiles)

        video_clip_path = os.path.join(stock_video_footage_folder, random_stock_footage_file)

        if not os.path.isfile(video_clip_path):
            raise FileNotFoundError(f"Video file '{video_clip_path}' not found.")

        video_clip = VideoFileClip(video_clip_path)

        video_duration = video_clip.duration

        if video_duration < short_duration:
            raise ValueError("Video duration is shorter than the audio duration.")

        start_time = random.uniform(0, video_duration - short_duration)

        segment_clip = video_clip.subclip(start_time, start_time + short_duration).set_audio(audio_clip)

        final_clip = CompositeVideoClip([segment_clip, subtitle_clip])

        current_date = datetime.now().strftime('%Y%m%d%H%M%S')

        final_clip_path = os.path.join(output_video_folder, f'{int(short_duration)}_{current_date}.mp4')

        temp_video_path = os.path.join(temp_file_folder, f'{int(short_duration)}_{current_date}.mp4')

        final_clip.write_videofile(final_clip_path, codec='libx264', audio_codec='aac', temp_audiofile=temp_video_path)

        os.remove(f'{skeletonFilePath}.mp3')
        os.remove(f'{skeletonFilePath}.srt')

        return True


    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def generate_AI_powered_video(text: str = ''):
    try:
        # generate mp3 and srt files and get the path to them
        audio_file_path = audioAI.get_mp3_from_text(text=text)

        # get the audio clip
        audio_clip = AudioFileClip(audio_file_path)

        short_duration = audio_clip.duration

        videoFootageFiles = os.listdir(stock_video_footage_folder)

        if not videoFootageFiles:
            raise ValueError("No video files found in the stock video footage folder.")

        random_stock_footage_file = random.choice(videoFootageFiles)

        video_clip_path = os.path.join(stock_video_footage_folder, random_stock_footage_file)

        if not os.path.isfile(video_clip_path):
            raise FileNotFoundError(f"Video file '{video_clip_path}' not found.")

        video_clip = VideoFileClip(video_clip_path)

        video_duration = video_clip.duration

        if video_duration < short_duration:
            raise ValueError("Video duration is shorter than the audio duration.")

        start_time = random.uniform(0, video_duration - short_duration)

        segment_clip = video_clip.subclip(start_time, start_time + short_duration).set_audio(audio_clip)

        subtitle_file_path = audioAI.generate_srt_from_mp3(audio_file_path=audio_file_path)

        generator = lambda txt: TextClip(txt, font="poppins", fontsize=50, color="white", method='caption',stroke_color="black", stroke_width=2, size=segment_clip.size)

        subtitle_clip = SubtitlesClip(subtitle_file_path, generator)

        final_clip = CompositeVideoClip([segment_clip, subtitle_clip])

        current_date = datetime.now().strftime('%Y%m%d%H%M%S')

        final_clip_path = os.path.join(output_video_folder, f'{int(short_duration)}_{current_date}.mp4')

        temp_video_path = os.path.join(temp_file_folder, f'{int(short_duration)}_{current_date}.mp4')

        final_clip.write_videofile(final_clip_path, codec='libx264', audio_codec='aac', temp_audiofile=temp_video_path)

        os.remove(audio_file_path)
        os.remove(subtitle_file_path)

        return True


    except Exception as e:
        print(f"An error occurred: {e}")
        return False
