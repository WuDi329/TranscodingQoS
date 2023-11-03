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
    # 这里print一下观察输出结果
    # 这里的逻辑有点问题，要找一个合适的dispatch方式，一方面方便测试，一方面方便实际应用。
    mac = helper.query_second_device()[0][0]
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
        command = "ffmpeg -y -i {} -c:v {} -b:v {} -c:a copy -f segment -segment_time 10 -segment_list {}/out.m3u8 -segment_format mpegts {}/output_%03d.ts".format(path, codec, bitrate, outputpath, outputpath)

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
    if videotask.mode == Mode.Normal:
        analyzer.measure(callback_func, contractid) 
    elif videotask.mode == Mode.Latency:
        analyzer.measure_latency(callback_func, contractid, outputpath)

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