from enums import Resolution, VideoCodec, AudioCodec
import uuid


class Video:
    def __init__(self, path: str, output_path: str, resolution: Resolution, videocodec: VideoCodec, bitrate, framerate, duration, audiocodec: AudioCodec) -> None:
        """
            创建一个video对象.
        """
        if not isinstance(resolution, Resolution):
            raise ValueError("当前不支持该分辨率")
        self._path = path
        self._outputpath = output_path
        self._vid = str(uuid.uuid1())
        self._resolution = resolution
        self._videocodec = videocodec
        # 这里的bitrate未必是标准的，因每个视频而异
        self._bitrate = bitrate
        self._framerate = framerate
        self._duration = duration
        self._audiocodec = audiocodec
        
    @property
    def vid(self):
        return self._vid

    @property
    def resolution(self):
        return self._resolution
    
    @property
    def path(self):
        return self._path
    
    @property
    def outputpath(self):
        return self._outputpath

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
        self._bitrate = value

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        self._framerate = value

    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        self._duration = value
    
    @property
    def audiocodec(self):
        return self._audiocodec
    
    @audiocodec.setter
    def audiocodec(self, value):
        self._audiocodec = value