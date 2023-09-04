from contextlib import contextmanager
import time
import datetime
from .qosmetric import QualityOfServiceMetric
from enums import Mode, AudioCodec
from .config import get_config_value, parse_config_file
from enums import VideoQualityKind, AudioQualityKind
from analyzer import VMAFAnalyzer, SSIMAnalyzer, PSNRAnalyzer, PESQAnalyzer
import os
from .videotask import VideoTask
from .qosmetric import QualityOfServiceMetric
from db.mysqlhelper import MySQLHelper
import threading


class NewThread(threading.Thread):
    def __init__(self, target, args):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
    
    def run(self):
        print('run运行时...')
        print(self.args)
        self.result = self.target(self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

class QoSAnalyzer:
    def __init__(self, videotask: VideoTask, outputpath: str): 
        self.origin_video_path = videotask.path
        self.output_video_path = outputpath
        # self.qos \= qos
        self.mode = videotask.mode
        self.vquality_map = {
            VideoQualityKind.VMAF: VMAFAnalyzer,
            VideoQualityKind.SSIM: SSIMAnalyzer,
            # 尚未实现
            # VideoQualityKind.MSSSIM: MSSSIMAnalyzer,
        }
        self.audiocodec = videotask.audiocodec
        self.aquality_map = {
            AudioQualityKind.PESQ: PESQAnalyzer
        }
        self.get_analyzer_config()
    
    def get_analyzer_config(self):
        """
            根据输入的Mode从配置文件中获取视频和音频分析工具类型

            Args:
                None

            Returns:
                None

        """
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "analyzer.ini")
        analyzer_lib = parse_config_file(file_path)
        # 获取具体视频和音频分析工具
        video_analyzer = get_config_value(analyzer_lib, self.mode.value, "video")
        audio_analyzer = get_config_value(analyzer_lib, self.mode.value, "audio")

        # 根据配置文件中的值，将字符串转换为枚举类型 
        self.video_analyzer_kind = VideoQualityKind(video_analyzer)
        self.audio_analyzer_kind = AudioQualityKind(audio_analyzer)

        video_analyzer_class = self.vquality_map[self.video_analyzer_kind]
        audio_analyzer_class = self.aquality_map[self.audio_analyzer_kind]

        self.video_analyzer = video_analyzer_class()
        self.audio_analyzer = audio_analyzer_class()

        print(self.video_analyzer)
        print(self.audio_analyzer)
        # self.qos = QualityOfService(video_analyzer, audio_analyzer)

    def wait_first_ts(self, outputpath: str, ):
        while not os.path.exists(os.path.join(outputpath, "output_000.ts")):
            time.sleep(0.05)
        print('output_000.ts已经出现，记录时间')
        return time.monotonic()

    # @contextmanager
    def measure(self, cb, contractid: str):
        # result = 
        origin_file_size = os.path.getsize(self.origin_video_path)
        start_time = time.monotonic()
        # try:
        cb()
        # finally:
        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(elapsed_time)
        output_file_size = os.path.getsize(self.output_video_path)
        videoquality = self.measure_video_quality()
        if self.audiocodec != AudioCodec.NONE:
            audioquality = self.measure_audio_quality()
        else:
            audioquality = None
        print(videoquality)
        print(audioquality)
        print("测量 finished")
        qosmetric =  QualityOfServiceMetric(contractid, start_time, elapsed_time, self.video_analyzer_kind, self.audio_analyzer_kind, origin_file_size, output_file_size, videoquality, audioquality)
        self.insert_metric_into_db(qosmetric)
        
    def measure_video_quality(self):
        return self.video_analyzer.analyze(self.origin_video_path, self.output_video_path)
    
    def measure_audio_quality(self):
        return self.audio_analyzer.analyze(self.origin_video_path, self.output_video_path)
    
    def insert_metric_into_db(self, qosmetric: QualityOfServiceMetric):
        helper = MySQLHelper()
        helper.connect()
        helper.insert_metric(qosmetric)
        helper.disconnect()

    def measure_latency(self, cb, contractid: str, outputpath: str):
        origin_file_size = os.path.getsize(self.origin_video_path)
        start_time = time.monotonic()
        t = NewThread(self.wait_first_ts, outputpath)
        t.start()
        # t.start()
        cb()
        t.join()
        end_time = time.monotonic() 
        first_ts_time = t.get_result()-start_time
        elapsed_time = end_time - start_time
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_video_path = self.merge_ts(outputpath)
        assert os.path.exists(output_video_path), "合并ts文件失败"
        output_file_size = os.path.getsize(output_video_path)
        self.output_video_path = os.path.join(outputpath, "output.mp4")
        videoquality = self.measure_video_quality()
        if self.audiocodec != AudioCodec.NONE:
            audioquality = self.measure_audio_quality()
        else:
            audioquality = None
        print("测量 finished")
        # 这里的metric可能要改一下
        print("start_time{}".format(start_time))
        print("first_ts_time{}".format(first_ts_time))
        print("elapsed_time{}".format(elapsed_time))
        print("origin_file_size{}".format(origin_file_size))
        print("output_file_size{}".format(output_file_size))
        print("video_analyzer_kind{}".format(self.video_analyzer_kind))
        print("videoquality{}".format(videoquality))
        print("audio_analyzer_kind{}".format(self.audio_analyzer_kind))
        print("audioquality{}".format(audioquality))
        # print(output_file_size)
        
    
    def merge_ts(self, outputpath: str):
        # 读取outputpath目录下的playlist.m3u8，获取ts文件列表
        playlist_path = os.path.join(outputpath, "playlist.m3u8")
        with open(playlist_path, "r") as f:
            lines = f.readlines()
        ts_list = []
        for line in lines:
            if line.startswith("output_") and line.endswith(".ts\n"):
                ts_list.append(line.strip())
        output_file_path = os.path.join(outputpath, 'ts_files.txt')
        with open(output_file_path, 'w') as f:
            for file in ts_list:
                f.write(f"file '{file}'\n")
        
        # 使用ffmpeg将ts文件合并为mp4文件
        output_video_path = os.path.join(outputpath, 'output.mp4')
        cmd = f"ffmpeg -f concat -safe 0 -i {output_file_path} -c copy {output_video_path}"
        os.system(cmd)
        return output_video_path
