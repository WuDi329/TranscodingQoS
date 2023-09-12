import subprocess
import sys
import time
import os
from transcode.measure import QoSAnalyzer
import threading

stop_event = threading.Event()

def handle_request(input):
    print ("Handling input: " + input)

def collect_latency():
    pass

def collect_bitrate_framerate(import_url):
    print("in collect_bitrate_framerate")
    print(import_url)
    cmd = "ffmpeg -i {} 2> temp.txt".format(import_url)
    os.system(cmd)
    cmd = "printf \"%s,%s\\n\" \"$(tail -n 4 temp.txt | head -n 1 | cut -d ',' -f 2)\" \"$(tail -n 2 temp.txt | head -n 1)\" >> res.txt"
    os.system(cmd)
    os.system("rm temp.txt")


def run_collect_bitrate_framerate(import_url):
    time.sleep(3)
    while not stop_event.is_set():
        collect_bitrate_framerate(import_url)
        time.sleep(9)

def handle_transcoding(command, rtmp, last):
    print("current traaaaaaaaaaaaaaaanscoding command:")
    print(rtmp)
    last = '"' + last + '"'
    start_time = time.time()
    command = command + " " + last

    thread = threading.Thread(target=run_collect_bitrate_framerate, args=(rtmp, ))
    thread.start()
    # with open("/home/wd/desktop/VideoQuality/command.txt", "w") as f:
    #     f.write(command)
    #     f.close()
    # print ("Handling input: " + input)
    os.system(command)
    stop_event.set()
    thread.join()
    end_time = time.time()
    transcoding_time = end_time - start_time
    print("Transcoding finished in {} seconds.".format(transcoding_time))
    # 创建文件，输出时间
    with open("/home/wd/desktop/VideoQuality/transcoding_time.txt", "w") as f:
        f.write(str(transcoding_time)+"\n")
        f.close()


if __name__ == "__main__":
    print(sys.argv[15])
    # os.system("echo 123 >> /home/wd/desktop/VideoQuality/temp.txt")
    # handle_transcoding(
    # start_time = time.time()
    with open("/home/wd/desktop/VideoQuality/curr_instruction.txt", "a") as f:
        f.write(" ".join(sys.argv[1:]))
        f.close()
    handle_transcoding(" ".join(sys.argv[1:-1]), sys.argv[-1].split("]")[-1], sys.argv[-1])
    # command = "ffmpeg -i rtmp://localhost:1935/live/stream -c:v libx264 -b:v 5M -c:a copy -f mpegts -muxdelay 0.001 -muxpreload 0.001 -y output_000.ts"
