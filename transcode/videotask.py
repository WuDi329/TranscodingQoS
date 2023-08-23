import uuid
from .task import Task
from .video import Video
# from db.mysqlhelper import MySQLHelper

class VideoTask:
    def __init__(self, video: Video, task: Task, taskid=None):
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
        if taskid != None:
            self._taskid = taskid
        else:
            self._taskid = str(uuid.uuid1())
        print("taskid: ", self._taskid)
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
        self._mode = task.mode

    @classmethod
    def create_task_from_db(result):
        print(result)
        # video = Video(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7])

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
    
    @property
    def mode(self):
        return self._mode
    
        
        