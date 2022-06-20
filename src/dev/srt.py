from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

generator = lambda txt: TextClip(txt, font='Arial', fontsize=60, color='red')
subtitles = SubtitlesClip("/Users/bijan/Movies/aayush/box5.srt", generator)
video = VideoFileClip("/Users/bijan/Movies/aayush/box5.mp4")
result = CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])
result.write_videofile("subtitles-test.mp4", fps=video.fps, temp_audiofile="tmp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
