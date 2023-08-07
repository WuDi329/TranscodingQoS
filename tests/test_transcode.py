import unittest
import sys
sys.path.append("/home/wudi/desktop/measureQuality/transcode/")
from transcode import read_video_info
from enums import Resolution, VideoCodec, Bitrate, AudioCodec


class TestReadVideoInfo(unittest.TestCase):
    def test_read_video_info(self):
        # 假设video_path是一个视频文件的路径
        video_path = "/dataset/dataset/reference_videos/basketball_10sec_1920x1080_24.mp4"

        # 调用read_video_info函数，并检查返回值是否符合预期
        expected_result = {
            "duration": 3600,
            "bitrate": Bitrate.KBPS_2000,
            "resolution": Resolution.HD,
            "codec": VideoCodec.H264,
            "audio_codec": AudioCodec.AAC
        }
        result = read_video_info(video_path)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()