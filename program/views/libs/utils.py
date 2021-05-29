import sys


def get_default_threads():
    threads = 80
    try:
        # params number input command line
        threads = int(sys.argv[1:][0])
    except:
        pass

    return threads


def get_youtube_video_urls():
    return [
    ]
