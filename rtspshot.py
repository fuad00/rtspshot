#!/usr/bin/env python3

from doctest import Example
import av
import re
import os
import sys
import datetime
import argparse

def file_exists(path):
    if os.path.exists(path):
        return path

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
				print(f"[+] Captured screenshot for {rtsp_url}")
				return file_path
			else:
				if tries < 2:
					container.close()
					tries += 1
					return get_screenshot(rtsp_url, tries)
				else:
					print(f"[-] Broken video stream or unknown issues with {rtsp_url}")
					return
	except (MemoryError, PermissionError, av.InvalidDataError) as e:
		print(f"[-] Missed screenshot of {rtsp_url}: {repr(e)}")
		if tries < 2:
			tries += 1
			return get_screenshot(rtsp_url, tries)
		else:
			print(
				f"[-] Missed screenshot {rtsp_url}",
			)
			return
	except Exception as e:
		print(f"[!] Fatal on {rtsp_url} :    #{repr(e)}")
		return
	
def main():
	args = parse_arguments()
	print(args)
# 	print("""RTSPshot - v0.0.1

# GENERAL OPTIONS:
#   -f              List of rtsp cams to screenshot (required)
#   -h              Show this help
# """)



# 	now = datetime.datetime.now()
# 	fold = now.strftime('%Y-%m-%d__%H-%M-%S')
# 	os.system(f"mkdir {fold}")
# 	with open("example.txt") as file:
# 		for line in file:
# 			get_screenshot(line.rstrip(), folder=fold)


def parse_arguments():
	parser = argparse.ArgumentParser(description="RTSPshot v1.0.0")

	parser.add_argument("-f", "--file", help="File with rtsp urls", type=file_exists, required=True)
	#TODO: parser.add_argument("-o", "--output", help="Output folder (creates folader with today's date by default)", type=file_exists, required=False)

	return parser.parse_args()


if __name__ == "__main__":
    main()
