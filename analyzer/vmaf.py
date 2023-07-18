from video_quality_analyzer import VideoQualityAnalyzer
from key_frame_extractor import KeyFrameExtractor
import os
import subprocess
import concurrent.futures
import time

class VMAFAnalyzer(VideoQualityAnalyzer):
    def analyze(self, origin_video, transcoded_video):
        # ...
        output_file = self._get_vmaf(origin_video, transcoded_video)
        self.showResult(output_file)

    def _get_vmaf(self, origin_video, transcoded_video):
        """
            读取原始视频和转码后视频的路径，执行ffmpeg vmaf命令，获取视频质量分析结果。
            这里默认开启多线程，线程数为8。

            Args:
                origin_video (str): 原始视频的路径.
                transcoded_video (str): 转码后视频的路径.

            Returns:
                output_file (str): 视频质量分析结果路径.

        """
        # ...
        command = "ffmpeg -nostats -i {} -i {} -lavfi \"[0:v][1:v]libvmaf=psnr=1:n_threads=8\" -loglevel info -f null - 2> {} ".format(transcoded_video, origin_video, transcoded_video.split(".")[0]+"-vmaf-result.txt")
        print("当前执行vmaf指令：{}".format(command))
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        return transcoded_video.split(".")[0]+"-vmaf-result.txt"
    
    def _run_vmaf(self, origin_video, transcoded_video, vmaf_path):
        command = 'ffmpeg -i "{}" -i "{}" -lavfi "[0:v][1:v]libvmaf=psnr=1:n_threads=8:log_path={}" -f null -'.format(transcoded_video, origin_video, vmaf_path)
        print("当前执行指令：{}".format(command))
        subprocess.run(command, shell=True)
    
    def key_frame_vmaf(self, origin_video, transcoded_video):
        """
            读取原始视频和转码后视频的路径，执行ffmpeg vmaf命令，获取视频质量分析结果。
            使用跳帧的方式，只对关键帧区间的帧进行vmaf分析。

            Args:
                origin_video (str): 原始视频的路径.
                transcoded_video (str): 转码后视频的路径.

            Returns:
                output_file (str): 视频质量分析结果路径.

        """
        key_extractor = KeyFrameExtractor(origin_video, transcoded_video)
        out_dir = key_extractor.extractFrame()
        source_dir = os.path.join(out_dir, "source")
        target_dir = os.path.join(out_dir, "target")
        vmaf_dir = os.path.join(out_dir, "vmaf")

        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for slip in sorted(os.listdir(source_dir)):
                futures.append(executor.submit(self._run_vmaf, source_dir + '/' + slip, target_dir + '/' + slip, vmaf_dir + '/' + slip.split(".")[0] + '.txt'))
            # 等待任务完成
            for future in futures:
                future.result()
        executor.shutdown()

        



    def showResult(self, output_file):
        """
            针对每个视频质量分析结果，提取视频质量数据，并且输出。

            Args:
                output_file (str): 视频质量分析结果路径.

            Returns:
                Null

        """
        with open(output_file, "r") as f:
            lines = f.readlines()
            last_line = lines[-1]
            elements = last_line.split()
            # print(elements)
            fifth_element = elements[5]
            print("VMAF分析结果：{}".format(fifth_element))
        f.close()

