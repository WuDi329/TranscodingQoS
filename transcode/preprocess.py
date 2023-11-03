from db.mysqlhelper import MySQLHelper
from enums import Resolution, VideoCodec, Bitrate, AudioCodec, Accelerator, Mode
from .task import Task
from .video import Video
from .videotask import VideoTask
from .transcode import dispatch_task
import subprocess
import json
import os

async def upload(video_path: str, task: Task):
    """
        

        Args:
            video_path (str): 视频的路径.
            task (Task): 转码任务.

    """
    video = read_video_info(video_path)
    print(video.framerate)
    videotask = generate_videotask(video, task)
    # 这里修改了代码逻辑，将具体的代码执行和生成任务分开
    # execute_transcode(videotask)
    await dispatch_task(videotask)

def extract_video_message(video_info: dict, video_path: str):
    """
        从视频信息中提取视频相关信息，返回由视频相关信息组成的对象。

        Args:
            video_info (dict): 视频信息.

        Returns:
            video (Video): 视频相关信息组成的对象.
    """
    outputpath = os.path.dirname(video_path)
    width = video_info["streams"][0]["width"]
    height = video_info["streams"][0]["height"]
    video_codec = video_info["streams"][0]["codec_name"]
    bitrate = video_info["streams"][0]["bit_rate"]
    framerate = video_info["streams"][0]["r_frame_rate"]
    duration = video_info["streams"][0]["duration"]
    audio_codec=video_info['streams'][1]['codec_name'] if len(video_info['streams']) > 1 else 'none'

    print(width)
    print(height)

    resolution = ""
    if width == 1920 and height == 1080:
        resolution = Resolution.FHD
    elif width == 1280 and height == 720:
        resolution = Resolution.HD
    elif width == 640 and height == 480:
        resolution = Resolution.SD
    else:
        # 暂时不支持其他分辨率的情况
        resolution = "undefined"

    print(resolution)
    
    # 暂时只考虑hevc和h264
    video_codec = VideoCodec.H264 if video_codec == "h264" else VideoCodec.H265
    # 暂时只考虑aac和none
    audio_codec = AudioCodec.NONE if audio_codec == "none" else AudioCodec.AAC


    video = Video(video_path, outputpath, resolution, video_codec, bitrate, framerate, duration, audio_codec)

    # 这里同样缺少video实例化的过程
    helper = MySQLHelper()
    helper.connect()
    helper.insert_video(video)
    print("Inserted video record with ID: ", video.vid)
    helper.disconnect()
    return video

def read_video_info(video_path: str):
    """
        读取视频信息，返回由视频相关信息组成的对象。

        Args:
            video_path (str): 视频的路径.

        Returns:
            rate (float): 视频的帧率.
            length (float): 视频的长度.
    """
    current_path = os.path.abspath(__file__)
    cmd = "ffprobe -loglevel error -print_format json -show_streams {} > test.json".format(video_path, os.path.join(current_path, "test.json"))
    print("当前执行读取视频信息指令：{}".format(cmd))
    # 这里修了个一个小bug，之前是异步执行，提交任务时准确性存疑
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

    video_info = {}
    with open("test.json", "r") as f:
        video_info = json.load(f)
    f.close()

    return extract_video_message(video_info, video_path)

def generate_videotask(video: Video, task: Task):
    # 这里缺少数据库实例化的过程
    videotask = VideoTask(video, task)
    helper = MySQLHelper()
    helper.connect()
    helper.insert_videotask(videotask)
    print("Inserted taskid record with ID: ", videotask.taskid)
    helper.disconnect()
    return videotask