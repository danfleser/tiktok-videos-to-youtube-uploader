import sys

from program.utils.libs.upload_youtube_selenium import YouTubeUploader


def start():
    cookie_dir = sys.argv[1:][0]
    youtube_uploader = YouTubeUploader(True, cookie_dir)

    youtube_uploader.remove_unwatched_videos(False, True)

    youtube_uploader.quit()


start()
