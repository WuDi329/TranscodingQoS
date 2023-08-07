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
        self.taskid = str(uuid.uuid1())
        self._vid = video.vid
        self._duration = video.duration
        self._origincodec = video.videocodec
        self._outputcodec = task.videocodec
        self._originresolution = video.resolution
        self._outputresolution = task.resolution
        self._bitrate = task.bitrate
        self._framerate = video.framerate
        
        