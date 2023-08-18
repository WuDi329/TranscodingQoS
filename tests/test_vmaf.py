import unittest
import sys
sys.path.append("/home/wudi/desktop/measureQuality/")
from analyzer.vmaf import VMAFAnalyzer

class TestVMAFAnalyzer(unittest.TestCase):
    def setUp(self):
        self.vmaf_analyzer = VMAFAnalyzer()

    def test_get_ssim(self):
        origin_video = "/home/wudi/desktop/measureQuality/tests/rabbit.mp4"
        transcoded_video = "/home/wudi/desktop/measureQuality/tests/rabbit-265.mp4"
        # self.vmaf_analyzer.key_frame_vmaf(origin_video, transcoded_video)
        self.vmaf_analyzer.analyze(origin_video, transcoded_video)

if __name__ == "__main__":

    # if __name__ == "__main__":语句检查test_ssim.py模块是否正在作为主程序运行。
    # 如果是，那么它将调用unittest.main()函数来运行所有测试。
    # 如果不是，那么它将不会运行任何测试。
    unittest.main()