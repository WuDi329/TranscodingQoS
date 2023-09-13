import subprocess
import sys
import time
import os
from transcode.measure import QoSAnalyzer
import threading
import re

stop_bitrate_event = threading.Event()
stop_latency_event = threading.Event()
base_dir = "/home/wd/record_dir/hls"

def handle_request(input):
    print ("Handling input: " + input)

def collect_latency(outputpath: str, stop, start_time):

    print(outputpath)

    # 收集首帧延迟
    while not os.path.exists(os.path.join(outputpath, "0.ts")):
        time.sleep(0.05)
    first_time = time.monotonic()
    print('0.ts已经出现，记录时间')


    

    print(first_time)

    current_ts_number = 1
    current_ts = str(current_ts_number) + ".ts"
    occur_time = []
    occur_time.append(first_time-start_time)
    record_time = []
    sum = 0
    while True :
        if stop():
            break
        # 进入循环 ，代表stop_latency_event没有被设置
        if os.path.exists(os.path.join(outputpath, current_ts)):
            current_time = time.monotonic()
            occur_time.append(current_time-start_time)
            # 记录当前ts片段出现时间
            print("{}已经出现，记录时间".format(current_ts))
            print(current_time)

            time.sleep(0.05)
            # 文件处理，获取m3u8文件中的ts时间
            with open(os.path.join(outputpath, "index.m3u8"), "r") as f:
                result = 0
                lines = f.readlines()
                last_line = lines[-2].strip()
                match = re.search(':(.*?),', last_line)
                if match:
                    result = match.group(1)
                    sum += float(result)
                    record_time.append(sum)
                    print("record 倒数第二行值 number")
                    print(result)

            f.close()
            current_ts_number += 1
            current_ts = str(current_ts_number) + ".ts"
            time.sleep(1)
    # 写入采集结果到文件中，格式为0.ts last_lines[0]
    # with open("/home/wd/desktop/VideoQuality/latency.txt", "w") as f:
    #     for i in range(len(occur_time)):
    #         f.write(f"{i}.ts  {occur_time[i]}")
    # f.close()
    for i in range(len(occur_time)):
        print(f"occur_time {i}.ts  {occur_time[i]}\n")
    for i in range(len(record_time)):
        print(f"record_time {i}.ts  {record_time[i]}\n")
    for i in range(len(occur_time)):
        print(f"latency {i}.ts  {occur_time[i]-record_time[i]}\n")

    # 当stop_latency_event被设置时，停止收集延迟
    # current_time = time.monotonic() 




def collect_bitrate_framerate(import_url):
    # print("in collect_bitrate_framerate")
    # print(import_url)
    cmd = "ffmpeg -i {} 2> temp.txt".format(import_url)
    os.system(cmd)
    cmd = "printf \"%s,%s\\n\" \"$(tail -n 4 temp.txt | head -n 1 | cut -d ',' -f 2)\" \"$(tail -n 2 temp.txt | head -n 1)\" >> res.txt"
    os.system(cmd)
    os.system("rm temp.txt")


def run_collect_bitrate_framerate(import_url):
    time.sleep(3)
    while not stop_bitrate_event.is_set():
        collect_bitrate_framerate(import_url)
        time.sleep(9)

def handle_transcoding(command, rtmp, last):
    print("current traaaaaaaaaaaaaaaanscoding command:")
    print(rtmp)
    work_dir = os.path.join(base_dir, last.split("/")[-1])
    last = '"' + last + '"'
    start_time = time.monotonic()
    command = command + " " + last
    stop_threads = False
    # bitrate_thread = threading.Thread(target=run_collect_bitrate_framerate, args=(rtmp, ))
    # bitrate_thread.start()

    latency_thread = threading.Thread(target=collect_latency, args=(work_dir, lambda : stop_threads, start_time))
    latency_thread.start()
    # with open("/home/wd/desktop/VideoQuality/command.txt", "w") as f:
    #     f.write(command)
    #     f.close()
    # print ("Handling input: " + input)
    os.system(command)
    # 设置latency 和 bitrate的停止标志位
    stop_threads = True
    # stop_bitrate_event.set()
    # bitrate_thread.join()
    latency_thread.join()
    end_time = time.monotonic()
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
