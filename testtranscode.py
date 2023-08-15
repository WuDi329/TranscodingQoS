from transcode.transcode import read_video_info, transcode
from enums import Resolution, VideoCodec, Bitrate
from transcode.task import Task

# read_video_info("/dataset/dataset/reference_videos/basketball_10sec_1920x1080_24.mp4")

task = Task(Resolution.FHD, VideoCodec.H264, Bitrate.ULTRA)

transcode("/dataset/WD-Dataset/ref/cartoon-bus.mp4",task)
