
from db.mysqlhelper import MySQLHelper
from transcode.videotask import VideoTask
import json
import os
from transcode.config import get_config_value, parse_config_file
import datetime
import sys
from transcode.capabilities import get_nvenc_capability
from enums import Resolution, VideoCodec, Bitrate, AudioCodec, Accelerator, Mode
import subprocess
from loguru import logger
import random


# 这里的代码改自transcode/transcode.py
def execute_vod_transcode(videotask: VideoTask, mac: str, contractid: str):

    command, outputpath = prepare_transcode(videotask, mac, contractid)
    logger.info(f"finish build {videotask.taskid} instruction: {command}.")
    # print(videotask.outputcodec)

    # 创建QoSAnalyzer对象
    # 但是，实际上的QoSAnalyzer评估，应该由实际server做一份，并且作为证明的一部分返回，但是并不应该在这里进行？
    # analyzer = QoSAnalyzer(videotask, outputpath)

    subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    logger.success(f"Transcode {videotask.taskid} finished.")

    #  这里把具体的transcode指令作为参数传入
    # callback_func = functools.partial(handle_transcode, command)
    # if videotask.mode == Mode.Normal:
    #     analyzer.measure(callback_func, contractid) 
    # elif videotask.mode == Mode.Latency:
    #     analyzer.measure_latency(callback_func, contractid, outputpath)

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

def prepare_transcode(videotask: VideoTask, mac: str, contractid: str):
    task_outputcodec = videotask.outputcodec
    task_resolution = videotask.outputresolution
    task_bitrate = videotask.bitrate
    accelerator = get_random_accelerator(task_outputcodec)
    logger.info(f"Selected {accelerator.value}  for {videotask.taskid}.")

    # 访问test.ini获取转码参数
    encode_lib = read_encode_ini()
    logger.info(f"encode_lib is {encode_lib}")
    # 获取具体编码库
    codec = get_config_value(encode_lib, task_outputcodec.value, accelerator.value)

    logger.info(f"Selected {codec}  for {videotask.taskid}.")
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
    # 暂时不考虑latency场景，假定所有的都是
    # elif videotask.mode == Mode.Latency:
    #     outputpath = os.path.join(videotask.outputpath, f"{filename}_{timestamp}")
    #     if not os.path.exists(outputpath):
    #         os.mkdir(outputpath)
    #     build_m3u8(outputpath, float(videotask.duration))
    #     command = "ffmpeg -y -i {} -c:v {} -b:v {} -c:a copy -f segment -segment_time 10 -segment_list {}/out.m3u8 -segment_format mpegts {}/output_%03d.ts".format(path, codec, bitrate, outputpath, outputpath)

    # print("当前command")
    # print(outputpath)
    return command, outputpath

def get_random_accelerator(videocodec: VideoCodec):
    """
        从capabilities.json中随机获取一个转码能力。

        Returns:
            accelerator (Accelerator): 转码能力.
    """
    logger.info(f"videocodec {videocodec.value}")
    capability = read_capability()
    logger.info(f"get capability: {capability}")
    capability = json.loads(capability)
    accelerators = capability[videocodec.value]
    logger.info(f"get accelerators: {accelerators}")
    config = random.choice(accelerators)
    if config == 'software':
        config = Accelerator.software
    elif config == 'nvidia':
        config =  Accelerator.nvidia
    elif config == 'intel':
        config =  Accelerator.intel
    print(config)
    return config

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
    logger.info(f"file_path is {file_path}")
    try:
        encode_lib = parse_config_file(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件{file_path}不存在")

    return encode_lib