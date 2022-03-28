#!/usr/bin/env python3

import av
import re
import os
import sys
import datetime


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
	if (len(sys.argv) < 2) or ("-f" not in sys.argv) or ("-h" in sys.argv):
		print("""RTSPshot - v0.0.1

GENERAL OPTIONS:
  -f              List of rtsp cams to screenshot (required)
  -h              Show this help
	""")
	else:
		for w in range(len(sys.argv)):
			if sys.argv[w] == "-f":
				if sys.argv[w] != sys.argv[-1]:
					if len(sys.argv[w+1]) > 0:
						try:
							now = datetime.datetime.now()
							fold = now.strftime('%Y-%m-%d__%H-%M-%S')
							os.system(f"mkdir {fold}")
							with open(sys.argv[w+1]) as file:
								for line in file:
									get_screenshot(line.rstrip(), folder=fold)
						except Exception as e:
							print(e)
				else:
					print("No list specified. See -h")
			else:
				pass
main()


