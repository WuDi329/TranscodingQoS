import uuid
from .task import Task
from .video import Video

class VideoTask:
    def __init__(self, video: Video, task: Task):
        """
            创建一个VideoTask对象.

            Args:
                taskid (): 任务ID.
                vid (): 视频ID，这里应该是video的外键.
                duration (float): 视频时间长度（秒）.
                codec (str): 视频编码方式.
                bitrate (int): 视频码率（kbps）.
                framerate (float): 视频帧率.


        """
        self._taskid = str(uuid.uuid1())
        self._path = video.path
        self._outputpath = video.outputpath
        self._vid = video.vid
        self._duration = video.duration
        self._origincodec = video.videocodec
        self._outputcodec = task.videocodec
        self._originresolution = video.resolution
        self._outputresolution = task.resolution
        self._audiocodec = video.audiocodec
        self._bitrate = task.bitrate
        self._framerate = video.framerate

    @property
    def vid(self):
        return self._vid
    
    @property
    def taskid(self):
        return self._taskid
    
    @property
    def path(self):
        return self._path
    
    @property
    def outputpath(self):
        return self._outputpath
    
    @property
    def outputcodec(self):
        return self._outputcodec
    
    @property
    def bitrate(self):
        return self._bitrate
    
    @property
    def audiocodec(self):
        return self._audiocodec
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def origincodec(self):
        return self._origincodec
    
    @property
    def originresolution(self):
        return self._originresolution
    
    @property
    def outputresolution(self):
        return self._outputresolution
    
    @property
    def framerate(self):
        return self._framerate
    
        
        