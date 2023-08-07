import unittest
import sys
sys.path.append("/home/wudi/desktop/measureQuality/config/")
import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_file_path = '/home/wudi/desktop/measureQuality/config/test_config.ini'
        with open(self.config_file_path, 'w') as f:
            f.write('[input]\ninput_file = input.mp4\n[input_quality]\nbitrate = 1000\n[output]\noutput_file = output.mp4\n[output_quality]\nbitrate = 2000\n')

    def tearDown(self) -> None:
        import os
        os.remove(self.config_file_path)

    def test_parse_config_file(self):
        config_dict = config.parse_config_file(self.config_file_path)
        self.assertEqual(config_dict['input']['input_file'], 'input.mp4')
        self.assertEqual(config_dict['input_quality']['bitrate'], '1000')
        self.assertEqual(config_dict['output']['output_file'], 'output.mp4')
        self.assertEqual(config_dict['output_quality']['bitrate'], '2000')

    def test_get_config_value(self):
        config_dict = config.parse_config_file(self.config_file_path)
        self.assertEqual(config.get_config_value(config_dict, 'input', 'input_file'), 'input.mp4')
        self.assertEqual(config.get_config_value(config_dict, 'input_quality', 'bitrate'), '1000')
        self.assertEqual(config.get_config_value(config_dict, 'output', 'output_file'), 'output.mp4')
        self.assertEqual(config.get_config_value(config_dict, 'output_quality', 'bitrate'), '2000')

    if __name__ == '__main__':
        unittest.main() 