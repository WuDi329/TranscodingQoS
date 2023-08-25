import pickle
from mq.message import Message
class TaskMessage(Message):
    def __init__(self, taskid: str, mac: str):
        """
            创建一个TaskMessage对象.

            Args:
                taskid (str): 任务的ID.
                mac (str): 设备的MAC地址.
        """
        self._taskid = taskid
        self._mac = mac

    @property
    def taskid(self):
        return self._taskid
    
    @property
    def mac(self):
        return self._mac
    
    def to_dict(self):
        """
            将TaskMessage对象转换为字典.

            Returns:
                dict (dict): TaskMessage对象转换的字典.
        """
        return {
            "taskid": self.taskid,
            "mac": self.mac
        }
    
    def to_bytestring(self):
        """
            将TaskMessage对象转换为字节流.

            Returns:
                bytestring (bytes): TaskMessage对象转换的字节流.
        """
        return pickle.dumps(self.to_dict())
    
    def decode(self, data: bytes):
        return pickle.loads(data)