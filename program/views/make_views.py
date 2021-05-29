import random
import socket
import time

import urllib3
from threading import Thread

from program.views.libs.utils import get_default_threads, get_youtube_video_urls
from program.views.view_link import start_view_video

urllib3.disable_warnings()
socket.setdefaulttimeout(800)


def start():
    youtube_urls = get_youtube_video_urls()

    random.shuffle(youtube_urls)

    threads = []
    # create threads
    for index in range(1, get_default_threads()):
        thread = Thread(target=start_view_video, args=(youtube_urls, ))
        thread.start()
        threads.append(thread)

        if index % 25 == 0:
            time.sleep(60 * 15)

    # wait threads
    for thread in threads:
        thread.join()

    # os.system("taskkill /IM chrome.exe /F")


start()
