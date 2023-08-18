from contextlib import contextmanager
import time
from .qos import QualityOfService
from enums import Mode, AudioCodec
from .config import get_config_value, parse_config_file
from enums import VideoQualityKind, AudioQualityKind
from analyzer import VMAFAnalyzer, SSIMAnalyzer, PSNRAnalyzer, PESQAnalyzer
import os
from .videotask import VideoTask

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
        video_analyzer_kind = VideoQualityKind(video_analyzer)
        audio_analyzer_kind = AudioQualityKind(audio_analyzer)

        video_analyzer_class = self.vquality_map[video_analyzer_kind]
        audio_analyzer_class = self.aquality_map[audio_analyzer_kind]

        self.video_analyzer = video_analyzer_class()
        self.audio_analyzer = audio_analyzer_class()

        print(self.video_analyzer)
        print(self.audio_analyzer)
        # self.qos = QualityOfService(video_analyzer, audio_analyzer)

    @contextmanager
    def measure(self):
        start_time = time.monotonic()
        try:
            yield
        finally:
            end_time = time.monotonic()
            elapsed_time = end_time - start_time
            print(elapsed_time)
            videoquality = self.measure_video_quality()
            if self.audiocodec != AudioCodec.NONE:
                audioquality = self.measure_audio_quality()
            else:
                audioquality = "None"
            print(videoquality)
            print(audioquality)
            print("测量 finished")
        
    def measure_video_quality(self):
        return self.video_analyzer.analyze(self.origin_video_path, self.output_video_path)
    
    def measure_audio_quality(self):
        return self.audio_analyzer.analyze(self.origin_video_path, self.output_video_path)


    # def measure(self):
    #     measure_video(self.origin_video_path, self.output_video_path, self.qos)
    #     measure_audio(self.origin_video_path, self.output_video_path, self.qos)
    #     return self.qos



# @contextmanager
# def measure_time(video_path: str, qos: QualityOfService):
#     # 记录开始时间
#     start_time = time.time()
#     try:
#         yield
#     finally:
#         end_time = time.time()
#         metric_value = end_time - start_time
        
# def measure_video(origin_video_path: str, output_video_path: str, qos: QualityOfService):
    

# def measure_audio(origin_video_path: str, output_video_path: str, qos: QualityOfService):
#     with measure_time(video_path, qos) as metric_value:
#         qos.audio_metric = metric_value
