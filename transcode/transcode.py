import subprocess
import os
from .capabilities import get_nvenc_capability
from . import config
import json
from .task import Task
from .video import Video
from .videotask import VideoTask
from enums import Resolution, VideoCodec, Bitrate, AudioCodec, Accelerator
import random
from .config import get_config_value, parse_config_file
import datetime
from db.mysqlhelper import MySQLHelper

def read_video_info(video_path: str):
    """
        读取视频信息，返回由视频相关信息组成的对象。

        Args:
            video_path (str): 视频的路径.

        Returns:
            rate (float): 视频的帧率.
            length (float): 视频的长度.
    """
    cmd = "ffprobe -loglevel error -print_format json -show_streams {} > test.json".format(video_path)
    print("当前执行读取视频信息指令：{}".format(cmd))
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    video_info = {}
    with open("test.json", "r") as f:
        video_info = json.load(f)
    f.close()

    return extract_video_message(video_info, video_path)
    

    
    # 这里需要额外连接数据库持久化？
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

def transcode(video_path: str, task: Task):
    """
        

        Args:
            video_path (str): 视频的路径.
            task (Task): 转码任务.

    """
    video = read_video_info(video_path)
    print(video.framerate)
    videotask = generate_videotask(video, task)
    execute_transcode(videotask)

    # video = Video(video_info["streams"][0]["r_frame_rate"], video_info["streams"][0]["duration"])

def generate_videotask(video: Video, task: Task):
    # 这里缺少数据库实例化的过程
    videotask = VideoTask(video, task)
    helper = MySQLHelper()
    helper.connect()
    helper.insert_videotask(videotask)
    print("Inserted taskid record with ID: ", videotask.taskid)
    helper.disconnect()
    return videotask

def read_capability():
    """
        读取capabilities.json，返回由转码能力组成的对象。

        Returns:
            capability (dict): 转码能力组成的对象.
    """
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(parent_path, "capabilities.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            capability = json.load(f)
        f.close()
    else:
        capability = get_nvenc_capability()
    return capability

def read_encode_ini():
    """
        读取encode.ini，返回由转码参数组成的对象。

        Returns:
            encode_lib (dict): 转码参数组成的对象.
    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, "test.ini")

    try:
        encode_lib = parse_config_file(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件{file_path}不存在")

    return encode_lib

# 具体的accelerator目前设定为随机
def execute_transcode(videotask: VideoTask):

    task_outputcodec = videotask.outputcodec
    task_resolution = videotask.outputresolution
    task_bitrate = videotask.bitrate
    accelerator = get_random_accelerator(task_outputcodec)

    # 访问test.ini获取转码参数
    encode_lib = read_encode_ini()
    # 获取具体编码库
    codec = get_config_value(encode_lib, task_outputcodec.value, accelerator.value)
    # 获取具体比特率
    bitrate = get_config_value(encode_lib, task_resolution.value, task_bitrate.value)

    path = videotask.path

    # 获取文件名和后缀
    filename, extension = os.path.splitext(os.path.basename(path))

    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    outputpath = os.path.join(videotask.outputpath, f"{filename}_{timestamp}{extension}")

    print("当前输出路径")
    print(outputpath)

    # 以下部分开始拼凑ffmpeg指令

    command = "ffmpeg -y -i {} -c:v {} -b:v {} -c:a copy {}".format(path, codec, bitrate, outputpath)
    print("当前执行指令")
    print(command)
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print("转码完成")



def get_random_accelerator(videocodec: VideoCodec):
    """
        从capabilities.json中随机获取一个转码能力。

        Returns:
            accelerator (Accelerator): 转码能力.
    """
    # 
    capability = read_capability()
    capability = json.loads(capability)

    accelerators = capability[videocodec.value]
    config = random.choice(accelerators)
    if config == 'software':
        config = Accelerator.software
    elif config == 'nvidia':
        config =  Accelerator.nvidia
    elif config == 'intel':
        config =  Accelerator.intel
    print(config)
    return config




# def generate_video_task(video_path: str, task: task):
#     """
#         生成视频任务，返回视频任务列表。

#         Returns:
#             video_tasks (list): 视频任务列表.
#     """



    # return float(rate.strip()), float(length.strip())/1000