import subprocess
import os
from .capabilities import get_nvenc_capability
from . import config
import json
from .task import Task
from .video import Video
from .videotask import VideoTask
from enums import Resolution, VideoCodec, Bitrate, AudioCodec, Accelerator, Mode
import random
from .config import get_config_value, parse_config_file
import datetime
from db.mysqlhelper import MySQLHelper
from .measure import QoSAnalyzer
from mq.mqhelper import MQUtil
from mq.taskmessage import TaskMessage
import functools

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
    current_path = os.path.abspath(__file__)
    cmd = "ffprobe -loglevel error -print_format json -show_streams {} > test.json".format(video_path, os.path.join(current_path, "test.json"))
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

# 修改函数名为upload
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
    

# 这里将会随机将task分配给一个节点
async def dispatch_task(videotask: VideoTask):
    """
        分配任务，将任务分配给一个节点。

        Args:
            videotask (VideoTask): 视频任务.
    """
    # 这里应当随机选择一个节点，但是在demo阶段只有一个节点，所以直接执行
    helper = MySQLHelper()
    helper.connect()
    mac = helper.query_first_device()[0][0]
    print(mac)
    helper.contract_task(videotask.taskid, mac)
    result = helper.search_mac_unfinished_videotasks(mac)
    print(result)
    helper.disconnect()

    # 这里使用mq通知节点消息
    mqhelper = MQUtil()
    await mqhelper.connect()
    task = TaskMessage(videotask.taskid, mac)
    await mqhelper.send_message("task_queue", task)
    await mqhelper.disconnect()

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

def prepare_transcode(videotask: VideoTask, mac: str, contractid: str):
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

    command = ""
    if videotask.mode == Mode.Normal:
        outputpath = os.path.join(videotask.outputpath, f"{filename}_{timestamp}{extension}")
        command = "ffmpeg -y -i {} -c:v {} -b:v {} -c:a copy {}".format(path, codec, bitrate, outputpath)
    elif videotask.mode == Mode.Latency:
        outputpath = os.path.join(videotask.outputpath, f"{filename}_{timestamp}")
        if not os.path.exists(outputpath):
            os.mkdir(outputpath)
        build_m3u8(outputpath, float(videotask.duration))
        command = "ffmpeg -y -i {} -c:v {} -b:v {} -c:a copy -f segment -segment -segment_time 10 -segment_list {}/out.m3u8 -segment_format mpegts {}/output_%03d.ts".format(path, codec, bitrate, outputpath, outputpath)

    print("当前command")
    print(outputpath)
    return command, outputpath

def handle_transcode(command: str):
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    print("转码完成")


def execute_transcode(videotask: VideoTask, mac: str, contractid: str):

    command, outputpath = prepare_transcode(videotask, mac, contractid)
    # print(videotask.outputcodec)


    # 创建QoSAnalyzer对象
    analyzer = QoSAnalyzer(videotask, outputpath)

    callback_func = functools.partial(handle_transcode, command)
    analyzer.measure(callback_func, contractid)
    # print(qosmetric)
    # helper = MySQLHelper()
    # helper.connect()
    # helper.insert_metric(qosmetric)
    # # helper.disconnect()
    
    # 这里需要更改数据库任务结果
    helper = MySQLHelper()
    helper.connect()
    helper.update_mac_task(videotask.taskid, mac)
    helper.disconnect()

def build_m3u8(outputpath: str, duration: float):
    ts_duration = 10
    ts_count = int(duration // ts_duration + (duration % ts_duration > 0))
        # 拼凑 playlist.m3u8 文件
    # 这里设置了最大时长10s
    with open(os.path.join(outputpath, "playlist.m3u8"), 'w') as f:
        f.write('#EXTM3U\n')
        f.write('#EXT-X-VERSION:3\n')
        f.write('#EXT-X-MEDIA-SEQUENCE:0\n')
        f.write('#EXT-X-ALLOW-CACHE:YES\n')
        f.write(f'#EXT-X-TARGETDURATION:10\n')
        for i in range(ts_count):
            ts_filename = f'output_{i:03d}.ts'
            ts_duration_actual = min(ts_duration, duration - i * ts_duration)
            f.write(f'#EXTINF:{ts_duration_actual:.6f},\n')
            f.write(f'{ts_filename}\n')
        f.write('#EXT-X-ENDLIST\n')



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

def create_task_from_db(contractid):
    helper = MySQLHelper()
    helper.connect()
    result = helper.search_specific_videotask(contractid)
    print(result)
    helper.disconnect()
    if result[0][3] == "1920x1080":
        resolution = Resolution.FHD
    elif result[0][3] == "1280x720":
        resolution = Resolution.HD
    elif result[0][3] == "640x480":
        resolution = Resolution.SD
    else:
        resolution = "undefined"

    if result[0][10] == "h264":
        videocodec = VideoCodec.H264
    elif result[0][10] == "h265":
        videocodec = VideoCodec.H265
    else:
        videocodec = "undefined"
    
    if result[0][11] == "ultra":
        bitrate = Bitrate.ULTRA
    elif result[0][11] == "high":
        bitrate = Bitrate.HIGH
    elif result[0][11] == "medium":
        bitrate = Bitrate.MEDIUM
    elif result[0][11] == "low":
        bitrate = Bitrate.LOW
    else:
        bitrate = "undefined"

    if result[0][12] == 'normal':
        mode = Mode.Normal
    elif result[0][12] == 'latency-critical':
        mode = Mode.Latency
    elif result[0][12] == 'live':
        mode = Mode.Live
    else:
        mode = "undefined"

    if result[0][8] == 'aac':
        audiocodec = AudioCodec.AAC
    elif result[0][8] == 'none':
        audiocodec = AudioCodec.NONE
    else:
        audiocodec = "undefined"

    video = Video(result[0][1], result[0][2], resolution, videocodec, result[0][5], result[0][6], result[0][7], audiocodec)
    task = Task(resolution, videocodec, bitrate, mode)
    videotask = VideoTask(video, task, result[0][0])
    return videotask


# def generate_video_task(video_path: str, task: task):
#     """
#         生成视频任务，返回视频任务列表。

#         Returns:
#             video_tasks (list): 视频任务列表.
#     """



    # return float(rate.strip()), float(length.strip())/1000