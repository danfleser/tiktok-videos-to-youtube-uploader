import sys

from program.utils.libs.upload_youtube_selenium import YouTubeUploader


def start():
    cookie_dir = sys.argv[1:][0]
    print(f"Starting bulk reply {cookie_dir}")
    youtube_uploader = YouTubeUploader(True, cookie_dir)

    youtube_uploader.bulk_comments_reply()

    youtube_uploader.quit()
    print(f"Finished bulk reply {cookie_dir}")


start()
