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

class QoSAnalyzer:
    def __init__(self, videotask: VideoTask, outputpath: str): 
        self.origin_video_path = videotask.path
        self.output_video_path = outputpath
        # self.qos = qos
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

    @contextmanager
    def measure(self, contractid: str):
        # result = 
        origin_file_size = os.path.getsize(self.origin_video_path)
        start_time = time.monotonic()
        # try:
        yield
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
