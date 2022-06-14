from moviepy.editor import *
#
import glob
# for f in glob.glob("/Users/bijan/Movies/aayush/*.mp4"):
#     print(f)

import fnmatch
import os

dir_name = "/Users/bijan/Movies/aayush/"
# files = os.listdir()
# print(files)

files = sorted( filter( os.path.isfile, glob.glob(dir_name + '*.mp4') ) )

print(files)

concatenate_videoclips(list(map(lambda f: VideoFileClip(f), files)))
final = concatenate_videoclips(clips)
final.ipython_display(width = 480)

from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio
# for f in files:
#     if fnmatch.fnmatch(file, '*.mp4'):
#         print(file)
#
# # loading video gfg
# clipx = VideoFileClip("geeks.mp4")
