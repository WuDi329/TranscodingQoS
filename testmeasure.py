from transcode.measure import QoSAnalyzer
from enums import Mode
# from enums import Resolution, VideoCodec, Bitrate
# from transcode.task import Task

# read_video_info("/dataset/dataset/reference_videos/basketball_10sec_1920x1080_24.mp4")

mode = Mode.Normal
qosanalyzer = QoSAnalyzer("/home/wudi/desktop/measureQuality", "/home/wudi/desktop/measureQuality", mode)
