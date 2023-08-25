import aio_pika
import asyncio
from mq.message import Message

class MQUtil:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        """
            初始化 MQUtil 类.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None

    async def connect(self):
        """
            建立到 RabbitMQ 服务器的连接，并创建一个通道（channel）.
        """
        try:
            # 使用 pika.PlainCredentials 类创建一个凭证对象
            self.connection = await aio_pika.connect_robust(
                host = self.host,
                port = self.port,
                login = self.username,
                password = self.password
            )
            # 指定连接 RabbitMQ 服务器的用户名和密码
            self.channel = await self.connection.channel()
        except aio_pika.exceptions.AMQPError as e:
            print(f"Failed to connect to RabbitMQ server: {e}")
            raise

    async def disconnect(self):
        """
            关闭 RabbitMQ 连接.
        """
        try:
            await self.connection.close()
        except AttributeError as e:
            print(f"Failed to close connection: {e}")
            raise

    async def declare_queue(self, queue_name):
        """
            声明一个队列.
        """
        try:
            queue = await self.channel.declare_queue(name=queue_name, durable=True)

            return queue
        except aio_pika.exceptions.AMQPChannelError as e:
            print(f"Failed to declare queue {queue_name}: {e}")
            raise

    async def send_message(self, queue_name, message: Message):
        """
            发送消息到指定的队列.
        """
        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message.to_bytestring()),
                routing_key=queue_name
            )
        except aio_pika.exceptions.AMQPChannelError as e:
            print(f"Failed to send message to queue {queue_name}: {e}")
            raise

    async def receive_message(self, queue_name, callback):
        """
            从指定的队列中接收消息，并调用指定的回调函数处理消息.
        """
        try:
            # 声明队列
            queue = await self.declare_queue(queue_name)

            # 注册回调函数
            await queue.consume(callback)

            # 开始消费
            print("Start consuming messages...")
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Failed to receive message from queue {queue_name}: {e}")
            raise