from transcode.preprocess import upload
from enums import Resolution, VideoCodec, Bitrate, Mode
from transcode.task import Task
import asyncio

# read_video_info("/dataset/dataset/reference_videos/basketball_10sec_1920x1080_24.mp4")

async def start():

    task = Task(Resolution.FHD, VideoCodec.H264, Bitrate.ULTRA, Mode.Normal)

    await upload("/home/wd/cartoon-swim.mp4",task)

if __name__ == "__main__":
    asyncio.run(start())

