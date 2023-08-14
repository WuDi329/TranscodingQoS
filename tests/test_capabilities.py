import unittest
import sys
sys.path.append("/home/wudi/desktop/measureQuality/transcode/")
from capabilities import get_nvenc_capability

class TestCapabilities(unittest.TestCase):
    def test_capabilities(self):
        capabilities = get_nvenc_capability()
        self.assertIn("h264_nvenc", capabilities)
        self.assertIn("hevc_nvenc", capabilities)

if __name__ == '__main__':
    unittest.main()