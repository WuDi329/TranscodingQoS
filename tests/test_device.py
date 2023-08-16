import unittest
from unittest.mock import patch
import sys
sys.path.append("/home/wudi/desktop/measureQuality/")
import transcode.device
from transcode.device import get_device_uuid

class TestDevice(unittest.TestCase):
    @patch('transcode.device.get_mac_address')
    def test_get_device_uuid(self, mock_get_mac_address):
        # 模拟 get_mac_address 函数返回的MAC地址
        mock_get_mac_address.return_value = '00:11:22:33:44:55'

        # 调用 get_device_uuid 函数
        device_uuid = get_device_uuid()

        # print(device_uuid)

        # 断言 get_device_uuid 函数返回的设备标识符是否正确
        self.assertEqual(device_uuid, '001122334455')

if __name__ == '__main__':
    unittest.main()