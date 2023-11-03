import asyncio
import grpc
import transcoding_pb2
import transcoding_pb2_grpc

from loguru import logger

# async def send_request(stub, name):



async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = transcoding_pb2_grpc.TranscoderStub(channel)
        # 创建任务
        response = await stub.DispatchVoDTask(transcoding_pb2.DispatchVoDRequest(
            taskid="7897vahuovanoi",
            originurl="/home/wd/cartoon-swim.mp4",
            outputurl="/home/wd/cartoon-swim.mp4",
            # outputcodec=1,
            outputresolution="1920x1080",
            # outputaudiocodec=1,
            outputframerate="24",
            # outputbitrate=0,
            videoinfo=transcoding_pb2.VideoInfo(
                vid="12312312",
                duration="468.93",
                origincodec=1,
                originresolution="1920x1080",
                # originaudiocodec=1,
                originframerate="24",
                originbitrate="180000"
        )))
        logger.info(f"Received back {response.taskid}")

if __name__ == "__main__":
    asyncio.run(run())
