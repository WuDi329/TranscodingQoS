from enums import VideoQualityKind
from enums import AudioQualityKind
from typing import Optional

class QualityOfServiceMetric:
    def __init__(self, contractid: str, starttime: float, executiontime: float, videoqualitykind: VideoQualityKind, audioqualitykind: AudioQualityKind, originfilesize: int, outputfilesize: int, videoquality: float, audioquality: Optional[float]):
        self._contractid = contractid
        self._starttime = starttime
        self._executiontime = executiontime
        self._videoqualitykind = videoqualitykind
        self._audioqualitykind = audioqualitykind
        self._originfilesize = originfilesize
        self._outputfilesize = outputfilesize
        self._videoquality = videoquality
        self._audioquality = audioquality if audioqualitykind != AudioQualityKind.NONE else None

    @property
    def executiontime(self):
        return self._executiontime
    
    @property
    def starttime(self):
        return self._starttime
    
    @property
    def contractid(self):
        return self._contractid
    
    @property
    def videoqualitykind(self):
        return self._videoqualitykind.value
    
    @property
    def audioqualitykind(self):
        return self._audioqualitykind.value
    
    @property
    def originfilesize(self):
        return self._originfilesize
    
    @property
    def outputfilesize(self):
        return self._outputfilesize
    
    @property
    def videoquality(self):
        return self._videoquality
    
    @property
    def audioquality(self):
        return self._audioquality
    
