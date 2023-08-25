class Message:
    def __init__(self, data):
        self.data = data
    
    def to_dict(self):
        """
            将消息对象转换为字符串类型.
        """
        pass

    def to_bytestring(self):
        """
            将消息对象转换为字节串类型.
        """
        pass

    def decode(self):
        """
            将字节串类型的消息转换为字符串类型.
        """
        pass