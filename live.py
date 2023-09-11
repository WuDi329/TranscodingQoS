import subprocess
import sys
import time
import os
from transcode.measure import QoSAnalyzer


def handle_request(input):
    print ("Handling input: " + input)


def handle_transcoding(command, last):
    print(command)
    last = '"' + last + '"'
    start_time = time.time()
    command = command + " " + last
    # with open("/home/wd/desktop/VideoQuality/command.txt", "w") as f:
    #     f.write(command)
    #     f.close()
    # print ("Handling input: " + input)
    os.system(command)
    end_time = time.time()
    transcoding_time = end_time - start_time
    print("Transcoding finished in {} seconds.".format(transcoding_time))
    # 创建文件，输出时间
    with open("/home/wd/desktop/VideoQuality/transcoding_time.txt", "w") as f:
        f.write(str(transcoding_time)+"\n")
        f.close()


if __name__ == "__main__":
    print(sys.argv[15])
    # handle_transcoding(
    # start_time = time.time()
    with open("/home/wd/desktop/VideoQuality/curr_instruction.txt", "a") as f:
        f.write(" ".join(sys.argv[1:]))
        f.close()
    handle_transcoding(" ".join(sys.argv[1:-1]), sys.argv[-1])
    # command = "ffmpeg -i rtmp://localhost:1935/live/stream -c:v libx264 -b:v 5M -c:a copy -f mpegts -muxdelay 0.001 -muxpreload 0.001 -y output_000.ts"
