import uuid
import socket
import fcntl
import struct

class Device(object):
    def __init__(self,):
        self._macaddress = self.get_device_uuid()

    @property
    def macaddress(self):
        return self._macaddress 

    def get_mac_address(self):
        """
            获取设备的MAC地址.

            Returns:
                mac_address (str): 设备的MAC地址.
        """
        # 获取设备的名称
        ifname = "eth0"

        # 获取设备的MAC地址
        with open('/sys/class/net/%s/address' % ifname) as f:
            mac_address = f.read().strip()

        return mac_address

    def get_device_uuid(self):
        """
            获取设备的唯一标识符.

            Returns:
                device_uuid (str): 设备的唯一标识符.
        """
        # 获取设备的MAC地址
        mac_address = self.get_mac_address()

        # 将MAC地址转换为UUID
        device_uuid = mac_address.replace(':', '').upper()

        return device_uuid

