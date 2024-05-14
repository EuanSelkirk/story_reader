import moviepy.editor as mpy
from moviepy.video.fx.all import crop

videoname = 'MegaRampUltraRealisticGraphicsGameplay4K'

clip = mpy.VideoFileClip(f"/Users/euan/Desktop/story_reader/files/stock_video_footage/{videoname}.mp4")
(w, h) = clip.size

crop_width = h * 9/16
# x1,y1 is the top left corner, and x2, y2 is the lower right corner of the cropped area.

x1, x2 = (w - crop_width)//2, (w+crop_width)//2
y1, y2 = 0, h
cropped_clip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)
# or you can specify center point and cropped width/height
# cropped_clip = crop(clip, width=crop_width, height=h, x_center=w/2, y_center=h/2)
cropped_clip.write_videofile(f'/Users/euan/Desktop/story_reader/files/stock_video_916/{videoname}.mp4')

#publish beta branch
