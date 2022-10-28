#!/usr/bin/env python3

from tqdm import tqdm
import concurrent.futures
from config import config
import av
import re
import os
import sys
import datetime
import argparse

def file_exists(path):
    if os.path.exists(path):
        return path
    else:
        print(f"{path} not found")
        sys.exit()

def escape_chars(s: str):
    return re.sub(r"[^\w\-_. ]", "_", s)

def _is_video_stream(stream):
    return (
        stream.profile is not None
        and stream.start_time is not None
        and stream.codec_context.format is not None
    )
    

def get_screenshot(rtsp_url: str, folder, tries=2):
    try:
        with av.open(
            rtsp_url,
            options={
                "rtsp_transport": "tcp",
                "rtsp_flags": "prefer_tcp",
                "stimeout": "3000000",
            },
            timeout=60.0,
        ) as container:
            stream = container.streams.video[0]
            if _is_video_stream(stream):
                file_name = escape_chars(f"{rtsp_url.lstrip('rtsp://')}.jpg")
                file_path = folder + "/" + file_name
                stream.thread_type = "AUTO"
                for frame in container.decode(video=0):
                    frame.to_image().save(file_path)
                    break
                #print(f"[+] Captured screenshot for {rtsp_url}")
                #return file_path
                return 1
            else:
                if tries < 2:
                    container.close()
                    tries += 1
                    return get_screenshot(rtsp_url, tries)
                else:
                    #print(f"[-] Broken video stream or unknown issues with {rtsp_url}")
                    return
    except (MemoryError, PermissionError, av.InvalidDataError) as e:
        #print(f"[-] Missed screenshot of {rtsp_url}: {repr(e)}")
        if tries < 2:
            tries += 1
            return get_screenshot(rtsp_url, tries)
        else:
            #print(f"[-] Missed screenshot {rtsp_url}",)
            return
    except Exception as e:
        #print(f"[!] Fatal on {rtsp_url} :    #{repr(e)}")
        return
    


def parse_arguments():
    parser = argparse.ArgumentParser(description=f"{config.big_title}",
        usage=f'{config.title}.py [-h] file',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", help="File with rtsp urls", type=file_exists)

    parser.add_argument("-t", "--threads", dest="threads", metavar='', help="screenshoting threads (default: 10)", default=10, type=int, required=False)
    parser.add_argument("-o", "--output", dest="fold", metavar='', help="output folder (default: today's date)", type=str, required=False)

    parser.add_argument('-v ', '--version', action='version', version=f"{config.title} {config.version}")

    return parser.parse_args()

def main():

    args = parse_arguments()

    if args.fold:
        fold = args.fold
    else:
        now = datetime.datetime.now()
        fold = now.strftime('%Y-%m-%d__%H-%M-%S')

    os.system(f"mkdir {fold}")
    with open(args.file) as file:

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for line in file:
                future = executor.submit(get_screenshot, line.rstrip(), fold)
                return_value = future.result()
                print(return_value)



if __name__ == "__main__":
    main()
