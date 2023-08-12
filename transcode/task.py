import sys
sys.path.append("/home/wudi/desktop/measureQuality/enums/")
from enums import Resolution, VideoCodec, Bitrate


class Task:
    def __init__(self, resolution: Resolution, videocodec: VideoCodec, bitrate: Bitrate) -> None:
        """
            创建一个task对象.
        """
        self._resolution = resolution
        self._videocodec = videocodec
        self._bitrate = bitrate

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Resolution):
            self._resolution = value
        else:
            raise ValueError("Invalid resolution value")

    @property
    def videocodec(self):
        return self._videocodec

    @videocodec.setter
    def videocodec(self, value):
        if isinstance(value, VideoCodec):
            self._videocodec = value
        else:
            raise ValueError("Invalid video codec value")

    @property
    def bitrate(self):
        return self._bitrate

    @bitrate.setter
    def bitrate(self, value):
        if isinstance(value, Bitrate):
            self._bitrate = value
        else:
            raise ValueError("Invalid bitrate value")