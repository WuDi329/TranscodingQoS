import sys
sys.path.append("/home/wudi/desktop/measureQuality/")
import argparse
import time
import threading
import pika
import sys
from mq.mqhelper import MQUtil
from mq.message import Message
import threading
import asyncio
from db.mysqlhelper import MySQLHelper
from db.tablehelper import ComplexTaskTable
from prettytable import PrettyTable
# sys.path.append("/home/wudi/desktop/measureQuality/client/")
# sys.path.append("/home/wudi/desktop/measureQuality/")
# from transcode.transcode import read_video_info, upload
from transcode.transcode import create_task_from_db, execute_transcode
from enums import Resolution, VideoCodec, Bitrate, Mode
from transcode.task import Task
from transcode.device import Device
from transcode.videotask import VideoTask

# 定义登录信息
login_info = {}

def login() -> None:
    """
        登录，获取token。

    """
    device = Device()
    login_info["mac"] = device.macaddress
    print("Login successfully.")

def logout() -> None:
    """
        登出，销毁token。

    """
    print("Logout successfully.")

def query():
    """
        查询设备是否有任务。

    """
    print("Querying task information...")
    helper = MySQLHelper()
    helper.connect()
    results = helper.search_mac_unfinished_videotasks(login_info["mac"])
    table = ComplexTaskTable.table
    table.clear_rows()
    for row in results:
        table.add_row(row)
    helper.disconnect()
    print(table)



def transcode(taskid):
    """
        转码。

    """
    print("Transcoding...")
    vt = create_task_from_db(taskid)
    execute_transcode(vt, login_info["mac"])
    # print(result)
    # VideoTask.create_task_from_db(taskid)
    

async def listen_task() -> None:
    """
        监听任务队列，如果有任务则调用callback执行任务。

    """
    print("Listening task queue.")
    mqutil = MQUtil()
    await mqutil.connect()
    await mqutil.receive_message("task_queue", handle_task)

# def handle_task(ch, method, properties, body) -> None: 

def handle_task(message: Message) -> None:

    """
        ch RabbitMQ channel 对象
        method RabbitMQ 消息传递方法
        properties RabbitMQ 消息属性
        body 消息内容
    """
    # 使用 body.decode() 方法将消息内容解码为字符串
    # message = body.decode()
    # 任务格式：taskid,video_path,task_name
    # 使用 split() 方法将字符串按照逗号分隔为三个部分，分别是任务 ID、视频文件路径和任务名称。
    # taskid, video_path, task_name = message.split(",")
    # task = Task(Resolution.FHD, VideoCodec.H264, Bitrate.ULTRA, Mode.Normal)
    # transcode(video_path, task)

    print("Received task.")
    # time.sleep(1)

    # 使用 ch.basic_ack() 方法确认消息已经被处理完毕，并将消息从队列中删除。
    # delivery_tag 参数代表了消息的传递标签，它是一个整数值，用于唯一标识消息。
    # RabbitMQ 会在消息被发送到消费者之前为每个消息分配一个唯一的 delivery_tag，
    # 消费者在处理完消息后需要调用 ch.basic_ack() 方法并传递相应的 delivery_tag，以便 RabbitMQ 可以将消息从队列中删除。
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    # print("Handling task.")
    # upload(task)

def start_listen_task():
    asyncio.run(listen_task())

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Transcoder Command Line Client")
    subparsers = parser.add_subparsers(dest="command")

    # 登录命令
    login_parser = subparsers.add_parser("login", help="Login")
    login_parser.set_defaults(func=login)

    # 注销命令
    logout_parser = subparsers.add_parser("logout", help="Logout")
    logout_parser.set_defaults(func=logout)

    # 查询任务信息命令
    query_parser = subparsers.add_parser("query", help="Query task information")
    query_parser.set_defaults(func=query)

    # 转码命令
    transcode_parser = subparsers.add_parser("transcode", help="Transcode video")
    transcode_parser.add_argument("video_path", help="Path to the video file")
    transcode_parser.add_argument("task_name", help="Name of the transcoding task")
    transcode_parser.set_defaults(func=transcode)

    # 监听任务指派命令
    t = threading.Thread(target= start_listen_task)
    t.start()
    # listen_parser = subparsers.add_parser("listen", help="Listen for task assignment")
    # listen_parser.set_defaults(func=listen_task)

    # 解析命令行参数
    args = parser.parse_args()

    # 执行命令
    if hasattr(args, "func"):
        args.func()
    # else:
        # 如果没有外界输入，程序一直在线
    while True:
        command = input("Enter command: ")
        if command == "logout":
            break
        elif command == "query":
            query()
        elif command.startswith("transcode"):
            _, taskid = command.split(" ")
            transcode(taskid)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
        
